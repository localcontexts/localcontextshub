from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail
from django.template.loader import render_to_string

from accounts.models import UserAffiliation
from notifications.models import CommunityNotification
from bclabels.models import BCNotice, BCLabel
from tklabels.models import TKNotice, TKLabel
from projects.models import ProjectContributors, Project

from bclabels.forms import CustomiseBCLabelForm, ApproveAndEditBCLabelForm
from tklabels.forms import CustomiseTKLabelForm, ApproveAndEditTKLabelForm
from projects.forms import CreateProjectForm, ProjectCommentForm

from bclabels.utils import check_bclabel_type
from tklabels.utils import check_tklabel_type

from .forms import *
from .models import *
from .utils import *

# Connect
@login_required(login_url='login')
def connect_community(request):
    return render(request, 'communities/connect-community.html')

# Create Community
@login_required(login_url='login')
def create_community(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.community_creator = request.user
            obj.save()

            template = render_to_string('snippets/community-application.html', { 'obj' : obj })
            send_mail(
                'New Community Application', 
                template, 
                settings.EMAIL_HOST_USER, 
                [settings.SITE_ADMIN_EMAIL], 
                fail_silently=False)

            return redirect('dashboard')
    else:
        form = CreateCommunityForm()
        return render(request, 'communities/create-community.html', {'form': form})

# Registry
def community_registry(request):
    communities = Community.objects.filter(is_approved=True, is_publicly_listed=True)

    if request.user.is_authenticated:
        current_user = UserAffiliation.objects.get(user=request.user)
        user_communities = current_user.communities.all()
        # all_requests = CommunityJoinRequest.objects.all()

        if request.method == 'POST':
            # TODO: Change the button so the user can only submit a request once.
            # Check if CommunityJoinRequest exists
            # If it exists, show different button
            buttonid = request.POST.get('commid')
            target_community = Community.objects.get(id=buttonid)
            main_admin = target_community.community_creator

            req = CommunityJoinRequest.objects.create(user_from=request.user, target_community=target_community, user_to=main_admin)
            req.save()

            return redirect('community-registry')
    else:
        return render(request, 'communities/community-registry.html', {'communities': communities})

    context = {
        'communities': communities,
        'user_communities': user_communities,
        # 'all_requests': all_requests,
    }
    return render(request, 'communities/community-registry.html', context)

# Dashboard / Activity
@login_required(login_url='login')
def community_dashboard(request, pk):
    community = Community.objects.get(id=pk)

    n = CommunityNotification.objects.filter(community=community)
    bcnotices = BCNotice.objects.filter(communities=community)
    tknotices = TKNotice.objects.filter(communities=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'notifications': n,
            'member_role': member_role,
            'bcnotices': bcnotices,
            'tknotices': tknotices,
            
        }
        return render(request, 'communities/community.html', context)

# Update Community / Settings
@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'editor' or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    
    else:
        update_form = UpdateCommunityForm(instance=community)
        if member_role == 'admin': # Only admins can change the form 
            if request.method == "POST" and request.FILES:
                update_form = UpdateCommunityForm(request.POST, request.FILES, instance=community)
                if update_form.is_valid():
                    update_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Updated!')
                else:
                    update_form = UpdateCommunityForm(instance=community)

        context = {
            'community': community,
            'update_form': update_form,
            'member_role': member_role,
            
        }
        return render(request, 'communities/update-community.html', context)

# Members
@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    return render(request, 'communities/members.html', {'community': community, 'member_role': member_role, })

# Add member
@login_required(login_url='login')
def add_member(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})

    else:
        if request.method == "POST":
            form = InviteMemberForm(request.POST or None)
            receiver = request.POST.get('receiver')
            user_check = checkif_community_in_user_community(receiver, community)
            
            if user_check == False: # If user is not community member
                check_invitation = checkif_invite_exists(receiver, community) # Check to see if invitation already exists

                if check_invitation == False: # If invitation does not exist, save form.
                    if form.is_valid():
                        obj = form.save(commit=False)
                        obj.sender = request.user
                        obj.status = 'sent'
                        obj.community = community
                        obj.save()

                        messages.add_message(request, messages.INFO, 'Invitation Sent!')
                        return render(request, 'communities/add-member.html', {'community': community, 'form': form,})

                else: 
                    messages.add_message(request, messages.INFO, 'This user has already been invited to this community!')
                    return render(request, 'communities/add-member.html', {'community': community, 'form': form,})
            else:
                messages.add_message(request, messages.ERROR, 'This user is already a member.')
                return render(request, 'communities/add-member.html', {'community': community, 'form': form,})
        else:
            form = InviteMemberForm()

    context = {
        'community': community,
        'form': form,
        'member_role': member_role,
        
    }
    return render(request, 'communities/add-member.html', context)

# Activity / Notices
@login_required(login_url='login')
def community_activity(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        bcnotices = BCNotice.objects.filter(communities=community)
        tknotices = TKNotice.objects.filter(communities=community)

        # Form: Notify project contributor if notice was seen
        if request.method == "POST" and "notify-btn" in request.POST:
            bcnotice_uuid = request.POST.get('bcnotice-uuid')
            tknotice_uuid = request.POST.get('tknotice-uuid')

            if bcnotice_uuid != None:
                bcnotice_status = request.POST.get('bcnotice-status')

                bcnotice = BCNotice.objects.get(unique_id=bcnotice_uuid)
                statuses = bcnotice.statuses.filter(community=community)

                for status in statuses:
                    if bcnotice_status == 'seen':
                        status.seen = True
                        status.save()
                    if bcnotice_status == 'pending':
                        status.seen = True
                        status.status = 'pending'
                        status.save()
                        #TODO:
                        #Send User Notification (if researcher) OR 
                        #Send Institution Notififcation
                    if bcnotice_status == 'not_pending':
                        status.seen = True
                        status.status = 'not_pending'
                        status.save()
                        #TODO:
                        #Send User Notification (if resaercher) OR 
                        #Send Institution Notififcation
                return redirect('community-activity', community.id)

            if tknotice_uuid != None:
                tknotice_status = request.POST.get('tknotice-status')

                tknotice = TKNotice.objects.get(unique_id=tknotice_uuid)
                statuses = tknotice.statuses.filter(community=community)

                for status in statuses:
                    if tknotice_status == 'seen':
                        status.seen = True
                        status.save()
                    if tknotice_status == 'pending':
                        status.seen = True
                        status.status = 'pending'
                        status.save()
                    if tknotice_status == 'not_pending':
                        status.seen = True
                        status.status = 'not_pending'
                        status.save()
                return redirect('community-activity', community.id)

        # Form: Add comment to notice
        elif request.method == "POST" and "add-comment-btn" in request.POST:
            project_id = request.POST.get('project-id')
            project = Project.objects.get(id=project_id)

            form = ProjectCommentForm(request.POST or None)

            if form.is_valid():
                data = form.save(commit=False)
                data.project = project
                data.sender = request.user
                data.community = community
                data.save()
                return redirect('community-activity', community.id)

        else:
            form = ProjectCommentForm()

            context = {
                'bcnotices': bcnotices,
                'tknotices': tknotices,
                'community': community,
                'member_role': member_role,
                
                'form': form,
            }
            return render(request, 'communities/activity.html', context)

# Labels Main
@login_required(login_url='login')
def community_labels(request, pk):
    community = Community.objects.get(id=pk)
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
            
        }
        return render(request, 'communities/labels.html', context)

# Select Labels to Customise
@login_required(login_url='login')
def select_label(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            bclabel_type = request.POST.get('bclabel-type')
            tklabel_type = request.POST.get('tk-label-type')
            
            # check if type already exists

            if bclabel_type:
                bctype = check_bclabel_type(bclabel_type)
                type_exists = BCLabel.objects.filter(community=community, label_type=bctype).exists()
                if type_exists:
                    return redirect('label-exists', community.id)
                else:
                    return redirect('customise-bclabel', community.id, bclabel_type)

            if tklabel_type:
                tktype = check_tklabel_type(tklabel_type)
                type_exists = TKLabel.objects.filter(community=community, label_type=tktype).exists()
                if type_exists:
                    return redirect('label-exists', community.id)
                else:
                    return redirect('customise-tklabel', community.id, tklabel_type)
        
        context = {
            'community': community,
            'member_role': member_role,
            
        }

        return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
def label_exists(request, pk):
    community = Community.objects.get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
            
        }
        return render(request, 'communities/label-exists.html', context)

# BC Label customisation process
@login_required(login_url='login')
def customise_bclabel(request, pk, label_type):
    community = Community.objects.get(id=pk)
    bc_type = check_bclabel_type(label_type)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            form = CustomiseBCLabelForm(request.POST)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.label_type = bc_type
                label_form.community = community
                label_form.created_by = request.user
                label_form.is_approved = False
                label_form.save()

                title = "A BC Label was customized by " + request.user.get_full_name()
                CommunityNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)
        else:
            form = CustomiseBCLabelForm()

        context = {
            'community': community,
            'label_type': label_type,
            'form': form,
            'member_role': member_role,
            
        }
        return render(request, 'communities/customise-bclabel.html', context)

# TK Label customisation process
@login_required(login_url='login')
def customise_tklabel(request, pk, label_type):
    community = Community.objects.get(id=pk)
    tk_type = check_tklabel_type(label_type)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            form = CustomiseTKLabelForm(request.POST)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.label_type = tk_type
                label_form.community = community
                label_form.created_by = request.user
                label_form.is_approved = False
                label_form.save()
                
                title = "A TK Label was customized by " + request.user.get_full_name()
                CommunityNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)
        else:
            form = CustomiseTKLabelForm()

        context = {
            'community': community,
            'label_type': label_type,
            'form': form,
            'member_role': member_role,
            'form': form,
            
        }
        return render(request, 'communities/customise-tklabel.html', context)

# Approve BC Label
@login_required(login_url='login')
def approve_bclabel(request, pk, label_id):
    community = Community.objects.get(id=pk)
    bclabel = BCLabel.objects.get(unique_id=label_id)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = ApproveAndEditBCLabelForm(instance=bclabel)
        if request.method == "POST":
            form = ApproveAndEditBCLabelForm(request.POST, instance=bclabel)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.is_approved = True
                label_form.approved_by = request.user
                label_form.save()
                title = "A BC Label was approved by " + request.user.get_full_name()
                CommunityNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)
                
                return redirect('community-labels', community.id)
        else:
            form = ApproveAndEditBCLabelForm(instance=bclabel)

        context = {
            'community': community,
            'bclabel': bclabel,
            'member_role': member_role,
            'form': form,
            
        }
        return render(request, 'communities/approve-bclabel.html', context)

# Approve TK Labels
@login_required(login_url='login')
def approve_tklabel(request, pk, label_id):
    community = Community.objects.get(id=pk)
    tklabel = TKLabel.objects.get(unique_id=label_id)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = ApproveAndEditTKLabelForm(instance=tklabel)
        if request.method == "POST":
            form = ApproveAndEditTKLabelForm(request.POST, instance=tklabel)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.is_approved = True
                label_form.approved_by = request.user
                label_form.save()

                title = "A TK Label was approved by " + request.user.get_full_name()
                CommunityNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)
        else:
            form = ApproveAndEditTKLabelForm(instance=tklabel)

        context = {
            'community': community,
            'tklabel': tklabel,
            'member_role': member_role,
            'form': form,
            
        }
        return render(request, 'communities/approve-tklabel.html', context)

# Projects Main
@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.get(id=pk)
    
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        notices = community.bcnotice_communities.all()
        contribs = ProjectContributors.objects.filter(community=community)

        context = {
            'community': community, 
            'member_role': member_role,
            'notices': notices,
            'contribs': contribs,
            
        }
        return render(request, 'communities/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    community = Community.objects.get(id=pk)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == 'POST':
            form = CreateProjectForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.project_creator = request.user
                obj.save()

                ProjectContributors.objects.create(project=obj, community=community)
                return redirect('community-projects', community.id)
        else:
            form = CreateProjectForm()
        
        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'bclabels': bclabels,
            'tklabels': tklabels,
            
        }

        return render(request, 'communities/create-project.html', context)

# Add labels to community created projects
@login_required(login_url='login')
def apply_project_labels(request, pk, project_id):
    community = Community.objects.get(id=pk)
    project = Project.objects.get(id=project_id)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            bclabels_selected = request.POST.getlist('checked-labels')
            tklabels_selected = request.POST.getlist('tk-checked-labels')

            for choice in bclabels_selected:
                label = BCLabel.objects.get(unique_id=choice)
                project.bclabels.add(label)
                
            for tkchoice in tklabels_selected:
                tklabel = TKLabel.objects.get(unique_id=tkchoice)
                project.tklabels.add(tklabel)
            
            return redirect('community-projects', community.id)

        context = {
            'community': community,
            'project': project,
            'bclabels': bclabels,
            'tklabels': tklabels,
            'member_role': member_role,
            
        }
        return render(request, 'communities/apply-labels.html', context)

# Appy Labels to Notices
@login_required(login_url='login')
def apply_notice_labels(request, pk, notice_id):
    community = Community.objects.get(id=pk)

    bcnotice_exists = BCNotice.objects.filter(unique_id=notice_id).exists()
    tknotice_exists = TKNotice.objects.filter(unique_id=notice_id).exists()

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if bcnotice_exists:
            bcnotice = BCNotice.objects.get(unique_id=notice_id)
            if request.method == "POST":
                # add community to project contributors
                contrib = ProjectContributors.objects.get(project=bcnotice.project)
                contrib.community = community
                contrib.save()

                # Gets ids of all checkboxes
                label_selected = request.POST.getlist('checkbox-label')

                for choice in label_selected:
                    bclabel_exists = BCLabel.objects.filter(unique_id=choice).exists()
                    tklabel_exists = TKLabel.objects.filter(unique_id=choice).exists()

                    if bclabel_exists:
                        bclabel = BCLabel.objects.get(unique_id=choice)
                        bcnotice.project.bclabels.add(bclabel)
                    if tklabel_exists:
                        tklabel = TKLabel.objects.get(unique_id=choice)
                        bcnotice.project.tklabels.add(tklabel)
                return redirect('community-projects', community.id)
            
            context = {
                'community': community,
                'bcnotice': bcnotice,
                'bclabels': bclabels,
                'tklabels': tklabels,
                'member_role': member_role,
                
            }
            return render(request, 'communities/apply-notice-labels.html', context)

        else:
            tknotice = TKNotice.objects.get(unique_id=notice_id)
            if request.method == "POST":
                # add community to project contributors
                contrib = ProjectContributors.objects.get(project=tknotice.project)
                contrib.community = community
                contrib.save()

                # Gets ids of all checkboxes
                label_selected = request.POST.getlist('checkbox-label')

                for choice in label_selected:
                    bclabel_exists = BCLabel.objects.filter(unique_id=choice).exists()
                    tklabel_exists = TKLabel.objects.filter(unique_id=choice).exists()

                    if bclabel_exists:
                        bclabel = BCLabel.objects.get(unique_id=choice)
                        tknotice.project.bclabels.add(bclabel)
                    if tklabel_exists:
                        tklabel = TKLabel.objects.get(unique_id=choice)
                        tknotice.project.tklabels.add(tklabel)
                return redirect('community-projects', community.id)
        
            context = {
                'community': community,
                'tknotice': tknotice,
                'bclabels': bclabels,
                'tklabels': tklabels,
                'member_role': member_role,
                
            }
            return render(request, 'communities/apply-notice-labels.html', context)

# Relationships
@login_required(login_url='login')
def community_relationships(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
            
        }
        return render(request, 'communities/relationships.html', context)

def restricted_view(request, pk):
    community = Community.objects.get(id=pk)

    return render(request, 'communities/restricted.html', {'community': community, })
