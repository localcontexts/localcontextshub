from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from localcontexts.utils import dev_prod_or_local
from projects.utils import add_to_contributors
from helpers.utils import *

from .models import *
from projects.models import Project, ProjectContributors, ProjectPerson, ProjectCreator
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import ProjectComment, ProjectStatus, Notice, InstitutionNotice, EntitiesNotified, Connections, OpenToCollaborateNoticeURL

from django.contrib.auth.models import User
from accounts.models import UserAffiliation

from projects.forms import *
from helpers.forms import ProjectCommentForm, OpenToCollaborateNoticeURLForm
from communities.forms import InviteMemberForm, JoinRequestForm
from .forms import *

from helpers.emails import *

@login_required(login_url='login')
def connect_institution(request):
    institution = True
    institutions = Institution.approved.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        institution_name = request.POST.get('organization_name')
        if Institution.objects.filter(institution_name=institution_name).exists():
            institution = Institution.objects.get(institution_name=institution_name)

            # If join request exists or user is already a member, display Error message
            request_exists = JoinRequest.objects.filter(user_from=request.user, institution=institution).exists()
            user_is_member = institution.is_user_in_institution(request.user)

            if request_exists or user_is_member:
                messages.add_message(request, messages.ERROR, "Either you have already sent this request or are currently a member of this institution.")
                return redirect('connect-institution')
            else:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user_from = request.user
                    data.institution = institution
                    data.user_to = institution.institution_creator
                    data.save()

                    # Send institution creator email
                    send_join_request_email_admin(request, data, institution)
                    messages.add_message(request, messages.SUCCESS, "Request to join institution sent!")
                    return redirect('connect-institution')
        else:
            messages.add_message(request, messages.ERROR, 'Institution not in registry')
            return redirect('connect-institution')

    context = { 'institution': institution, 'institutions': institutions, 'form': form,}
    return render(request, 'institutions/connect-institution.html', context)

@login_required(login_url='login')
def preparation_step(request):
    institution = True
    return render(request, 'accounts/preparation.html', { 'institution': institution })

@login_required(login_url='login')
def create_institution(request):
    form = CreateInstitutionForm(request.POST or None)
    noror_form = CreateInstitutionNoRorForm(request.POST or None)

    if request.method == 'POST':
        affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user)

        if 'create-institution-btn' in request.POST:
            if form.is_valid():
                name = request.POST.get('institution_name')
                data = form.save(commit=False)

                if Institution.objects.filter(institution_name=name).exists():
                    messages.add_message(request, messages.ERROR, 'An institution by this name already exists.')
                    return redirect('create-institution')
                else:
                    data.institution_name = name
                    data.institution_creator = request.user

                    # If in test site, approve immediately, skip confirmation step
                    if dev_prod_or_local(request.get_host()) == 'DEV':
                        data.is_approved = True
                        data.save()
                        
                        # Add to user affiliations
                        affiliation.institutions.add(data)
                        affiliation.save()

                        # Create a Connections instance
                        Connections.objects.create(institution=data)
                        return redirect('dashboard')
                    else:
                        data.save()

                        # Add to user affiliations
                        affiliation.institutions.add(data)
                        affiliation.save()

                        # Create a Connections instance
                        Connections.objects.create(institution=data)
                        return redirect('confirm-institution', data.id)
        elif 'create-institution-noror-btn' in request.POST:
            if noror_form.is_valid():
                data = noror_form.save(commit=False)
                data.institution_creator = request.user
                data.is_ror = False
                data.save()

                # Add to user affiliations
                affiliation.institutions.add(data)
                affiliation.save()

                #  Create a Connections instance
                Connections.objects.create(institution=data)
                return redirect('confirm-institution', data.id)
    return render(request, 'institutions/create-institution.html', {'form': form, 'noror_form': noror_form,})

@login_required(login_url='login')
def confirm_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)

    form = ConfirmInstitutionForm(request.POST or None, request.FILES, instance=institution)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            # If in test site, approve immediately, skip confirmation step
            if dev_prod_or_local(request.get_host()) == 'DEV':
                data.is_approved = True
                data.save()
                return redirect('dashboard')
            else:
                data.save()
                send_hub_admins_application_email(request, institution, data)
                return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'institution': institution,})

def public_institution_view(request, pk):
    institution = Institution.objects.get(id=pk)
    created_projects = ProjectCreator.objects.filter(institution=institution)
    notices = Notice.objects.filter(institution=institution)
    projects = []

    for p in created_projects:
        if p.project.project_privacy == 'Public':
            projects.append(p.project)

    context = {
        'institution': institution,
        'projects' : projects,
        'notices': notices,
    }
    return render(request, 'public.html', context)

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')

    else:
        if request.method == "POST":
            update_form = UpdateInstitutionForm(request.POST, request.FILES, instance=institution)
            if update_form.is_valid():
                update_form.save()
                messages.add_message(request, messages.SUCCESS, 'Updated!')
                return redirect('update-institution', institution.id)
        else:
            update_form = UpdateInstitutionForm(instance=institution)

        context = {
            'institution': institution,
            'update_form': update_form,
            'member_role': member_role,
        }

        return render(request, 'institutions/update-institution.html', context)

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('public-institution', institution.id)
    else:
        urls = OpenToCollaborateNoticeURL.objects.filter(institution=institution)
        form = OpenToCollaborateNoticeURLForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.institution = institution
                data.save()
            return redirect('institution-notices', institution.id)

        context = {
            'institution': institution,
            'member_role': member_role,
            'form': form,
            'urls': urls,
        }
        return render(request, 'institutions/notices.html', context)

# Members
@login_required(login_url='login')
def institution_members(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        join_requests_count = JoinRequest.objects.filter(institution=institution).count()
        form = InviteMemberForm(request.POST or None)
        if request.method == 'POST':
            if 'change_member_role_btn' in request.POST:
                current_role = request.POST.get('current_role')
                new_role = request.POST.get('new_role')
                user_id = request.POST.get('user_id')
                member = User.objects.get(id=user_id)
                change_member_role(institution, member, current_role, new_role)
                return redirect('institution-members', institution.id)
            else:
                receiver = request.POST.get('receiver')
                user_in_institution = is_organization_in_user_affiliation(receiver, institution)

                if not user_in_institution: # If user is not an institution member
                    invitation_exists = InviteMember.objects.filter(receiver=receiver, institution=institution).exists() # Check to see if invitation already exists
                    join_request_exists = JoinRequest.objects.filter(user_from=receiver, institution=institution).exists() # Check to see if join request already exists

                    if not invitation_exists and not join_request_exists: # If invitation and join request does not exist, save form
                        if form.is_valid():
                            data = form.save(commit=False)
                            data.sender = request.user
                            data.status = 'sent'
                            data.institution = institution
                            data.save()
                            # Send email to target user
                            send_institution_invite_email(request, data, institution)
                            messages.add_message(request, messages.INFO, 'Invitation Sent!')
                            return redirect('institution-members', institution.id)
                    else: 
                        messages.add_message(request, messages.INFO, 'The user you are trying to add has already been invited to this institution.')
                else:
                    messages.add_message(request, messages.ERROR, 'The user you are trying to add is already a member of this institution.')

        context = { 
            'institution': institution,
            'form': form,
            'member_role': member_role,
            'join_requests_count': join_requests_count,
        }    
        return render(request, 'institutions/members.html', context)

@login_required(login_url='login')
def member_requests(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        join_requests = JoinRequest.objects.filter(institution=institution)
        member_invites = InviteMember.objects.filter(institution=institution)
        
        if request.method == 'POST':
            selected_role = request.POST.get('selected_role')
            join_request_id = request.POST.get('join_request_id')

            accepted_join_request(institution, join_request_id, selected_role)
            messages.add_message(request, messages.SUCCESS, 'You have successfully added a new member!')
            return redirect('institution-member-requests', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution,
            'join_requests': join_requests,
            'member_invites': member_invites,
        }
        return render(request, 'institutions/member-requests.html', context)

@login_required(login_url='login')
def delete_join_request(request, pk, join_id):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('institution-member-requests', institution.id)
    
@login_required(login_url='login')
def remove_member(request, pk, member_id):
    institution = Institution.objects.prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in institution.admins.all():
        institution.admins.remove(member)
    if member in institution.editors.all():
        institution.editors.remove(member)
    if member in institution.viewers.all():
        institution.viewers.remove(member)

    # remove institution from userAffiliation instance
    affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=member)
    affiliation.institutions.remove(institution)

    # Delete join request for this institution if exists
    if JoinRequest.objects.filter(user_from=member, institution=institution).exists():
        join_request = JoinRequest.objects.get(user_from=member, institution=institution)
        join_request.delete()

    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('institution-members', institution.id)

# Projects: all 
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor
        projects_list = []

        institution_projects = ProjectCreator.objects.filter(institution=institution) # projects created by institution

        for p in institution_projects:
            projects_list.append(p.project)

        institution_notified = EntitiesNotified.objects.select_related('project').prefetch_related('communities', 'researchers').filter(institutions=institution)
        for n in institution_notified:
            projects_list.append(n.project)
        
        contribs = ProjectContributors.objects.select_related('project').filter(institutions=institution)
        for c in contribs:
            projects_list.append(c.project)

        projects = list(set(projects_list))
        
        form = ProjectCommentForm(request.POST or None)
  
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_with_labels(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor
        projects_list = []

        for p in ProjectCreator.objects.select_related('project').filter(institution=institution): # projects created by institution
            if p.project.has_labels():
                projects_list.append(p.project)

        for n in EntitiesNotified.objects.select_related('project').filter(institutions=institution):
            if n.project.has_labels():
                projects_list.append(n.project)
        
        for c in ProjectContributors.objects.select_related('project').filter(institutions=institution):
            if c.project.has_labels():
                projects_list.append(c.project)

        projects = list(set(projects_list))
        
        form = ProjectCommentForm(request.POST or None)
  
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects-labels', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_with_notices(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor
        projects_list = []

        for p in ProjectCreator.objects.select_related('project').filter(institution=institution): # projects created by institution
            if not p.project.has_labels():
                projects_list.append(p.project)

        for n in EntitiesNotified.objects.select_related('project').filter(institutions=institution):
            if not n.project.has_labels():
                projects_list.append(n.project)
        
        for c in ProjectContributors.objects.select_related('project').filter(institutions=institution):
            if not c.project.has_labels():
                projects_list.append(c.project)

        projects = list(set(projects_list))
        
        form = ProjectCommentForm(request.POST or None)
  
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects-notices', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_creator(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        projects_list = []
        
        for p in ProjectCreator.objects.select_related('project').filter(institution=institution): # projects created by institution
            projects_list.append(p.project)
        
        projects = list(set(projects_list))

        form = ProjectCommentForm(request.POST or None)
  
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects-creator', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_contributor(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for projects where institution is contributor but not creator
        projects_list = []
        created_projects = []

        for x in ProjectContributors.objects.select_related('project').filter(institutions=institution):
            projects_list.append(x.project)

        for c in ProjectCreator.objects.select_related('project').filter(institution=institution):
            created_projects.append(c.project)

        # remove projects that were created by the institution
        for p in created_projects:
            if p in projects_list:
                projects_list.remove(p)

        projects = list(set(projects_list))
        
        form = ProjectCommentForm(request.POST or None)
  
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects-contributor', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return redirect('restricted')
    else:
        if request.method == 'GET':
            form = CreateProjectForm(request.GET or None)
            formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
        elif request.method == "POST":
            form = CreateProjectForm(request.POST)
            formset = ProjectPersonFormset(request.POST)

            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user
                data.save()
                
                # Add project to institution projects
                ProjectCreator.objects.create(institution=institution, project=data)

                #Create EntitiesNotified instance for the project
                EntitiesNotified.objects.create(project=data)

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, institution, data, None, None)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get project contributors instance and add institution
                contributors = ProjectContributors.objects.get(project=data)
                contributors.institutions.add(institution)
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)

                # Format and send notification about the created project
                truncated_project_title = str(data.title)[0:30]
                name = get_users_name(data.project_creator)
                title = f'A new project was created by {name}: {truncated_project_title} ...'
                ActionNotification.objects.create(title=title, notification_type='Projects', sender=data.project_creator, reference_id=data.unique_id, institution=institution)
                return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'form': form,
            'formset': formset,
            'member_role': member_role,
        }
        return render(request, 'institutions/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, institution_id, project_uuid):
    institution = Institution.objects.get(id=institution_id)
    project = Project.objects.get(unique_id=project_uuid)
    notice_exists = Notice.objects.filter(project=project).exists()
    institution_notice_exists = InstitutionNotice.objects.filter(project=project).exists()

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return redirect('restricted')
    else:
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.get(project=project)


        if notice_exists:
            notice = Notice.objects.get(project=project)
        else:
            notice = None
        
        if institution_notice_exists:
            institution_notice = InstitutionNotice.objects.get(project=project)
        else:
            institution_notice = None

        if request.method == 'POST':
            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)

                # Which notices were selected to change
                notices_selected = request.POST.getlist('checkbox-notice')
                # Pass any existing notices as well as newly selected ones
                create_notices(notices_selected, institution, data, notice, institution_notice)

            return redirect('institution-projects', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'notice': notice, 
            'institution_notice': institution_notice,
            'form': form,
            'formset': formset,
            'contributors': contributors,
        }
        return render(request, 'institutions/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, proj_id):
    institution = Institution.objects.select_related('institution_creator').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels', 'project_status').get(id=proj_id)
        entities_notified = EntitiesNotified.objects.get(project=project)
        communities = Community.approved.all()
        
        if request.method == "POST":
            # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            communities_selected = request.POST.getlist('selected_communities')
            message = request.POST.get('notice_message')

            # Reference ID and title for notification
            reference_id = str(project.unique_id)
            title =  str(institution.institution_name) + ' has notified you of a Project.'

            for community_id in communities_selected:
                # Add communities that were notified to entities_notified instance
                community = Community.objects.get(id=community_id)
                entities_notified.communities.add(community)

                # Create project status, first comment and  notification
                ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                ProjectComment.objects.create(project=project, community=community, sender=request.user, message=message)
                ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)
                entities_notified.save()

                # Create email 
                send_email_notice_placed(project, community, institution)
            
            return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'project': project,
            'communities': communities,
            'member_role': member_role,
        }
        return render(request, 'institutions/notify.html', context)

@login_required(login_url='login')
def connections(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        connections = Connections.objects.get(institution=institution)
        context = {
            'member_role': member_role,
            'institution': institution,
            'connections': connections,
        }
        return render(request, 'institutions/connections.html', context)
