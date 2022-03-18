from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.utils import add_to_contributors
from helpers.utils import set_notice_defaults, dev_prod_or_local

from communities.models import Community
from notifications.models import ActionNotification
from helpers.models import ProjectStatus, ProjectComment, Notice, EntitiesNotified, Connections
from projects.models import ProjectContributors, Project, ProjectPerson

from projects.forms import *
from helpers.forms import ProjectCommentForm

from helpers.emails import *

from .models import Researcher
from .forms import *
from .utils import *

@login_required(login_url='login')
def connect_researcher(request):
    researcher = is_user_researcher(request.user)
    form = ConnectResearcherForm(request.POST or None)
    
    if researcher == False:
        if request.method == "POST":
            if form.is_valid():
                orcid_id = request.POST.get('orcidId')
                orcid_token = request.POST.get('orcidIdToken')
                
                data = form.save(commit=False)
                data.user = request.user
                data.orcid_auth_token = orcid_token
                data.orcid = orcid_id
                data.save()

                # Create a Connections instance
                Connections.objects.create(researcher=data)

                # Mark current user as researcher
                request.user.profile.is_researcher = True
                request.user.profile.save()

                # Send support an email in prod only about a Researcher signing up
                if dev_prod_or_local(request.get_host()) == 'PROD':
                    send_email_to_support(data)
                    
                return redirect('dashboard')

        return render(request, 'researchers/connect-researcher.html', {'form': form})
    else:
        return redirect('researcher-projects', researcher.id)

@login_required(login_url='login')
def update_researcher(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        if request.method == 'POST':
            update_form = UpdateResearcherForm(request.POST, request.FILES, instance=researcher)

            if update_form.is_valid():
                data = update_form.save(commit=False)
                data.save()

                messages.add_message(request, messages.SUCCESS, 'Updated!')
                return redirect('researcher-update', researcher.id)
        else:
            update_form = UpdateResearcherForm(instance=researcher)
        
        context = {
            'update_form': update_form,
            'researcher': researcher,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/update-researcher.html', context)

@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.prefetch_related('projects').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        context = {
            'researcher': researcher,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/notices.html', context)


@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.prefetch_related('projects', 'user').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        # researcher projects + 
        # projects researcher has been notified of + 
        # projects where researcher is contributor
        projects_list = []
        researcher_projects = researcher.projects.prefetch_related('bc_labels', 'tk_labels').all()
        for p in researcher_projects:
            projects_list.append(p)

        researcher_notified = EntitiesNotified.objects.select_related('project').prefetch_related('communities', 'institutions').filter(researchers=researcher)
        for n in researcher_notified:
            projects_list.append(n.project)
        
        contribs = ProjectContributors.objects.select_related('project').filter(researchers=researcher)
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
                
                return redirect('researcher-projects', researcher.id)

        context = {
            # 'researcher_notified': researcher_notified,
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.prefetch_related('projects').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        if request.method == "GET":
            form = CreateProjectForm(request.POST or None)
            formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
        elif request.method == "POST":
            form = CreateProjectForm(request.POST)
            formset = ProjectPersonFormset(request.POST)

            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user
                data.save()
                # Add project to researcher projects
                researcher.projects.add(data)

                #Create EntitiesNotified instance for the project
                EntitiesNotified.objects.create(project=data)

                notices_selected = request.POST.getlist('checkbox-notice')
                if len(notices_selected) > 1:
                    notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_researcher=researcher, project=data)
                    set_notice_defaults(notice)
                else:
                    for selected in notices_selected:
                        if selected == 'bcnotice':
                            notice = Notice.objects.create(notice_type='biocultural', placed_by_researcher=researcher, project=data)
                            set_notice_defaults(notice)
                        elif selected == 'tknotice':
                            notice = Notice.objects.create(notice_type='traditional_knowledge', placed_by_researcher=researcher, project=data)
                            set_notice_defaults(notice)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get project contributors instance and add researcher to it
                contributors = ProjectContributors.objects.get(project=data)
                contributors.researchers.add(researcher)
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)
                
                # Send notification
                title = 'Your project has been created, remember to notify a community of your project.'
                ActionNotification.objects.create(title=title, sender=request.user, notification_type='Projects', researcher=researcher, reference_id=data.unique_id)

                return redirect('researcher-projects', researcher.id)

        context = {
            'researcher': researcher,
            'form': form,
            'formset': formset,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, researcher_id, project_uuid):
    researcher = Researcher.objects.get(id=researcher_id)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        project = Project.objects.get(unique_id=project_uuid)
        notice_exists = Notice.objects.filter(project=project)
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.get(project=project)

        # Check to see if notice exists for this project and pass to template
        if notice_exists:
            notice = Notice.objects.get(project=project)
        else:
            notice = None

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
                # If both notices were selected, check to see if notice exists
                # If not, create new notice delete old one
                if len(notices_selected) > 1:
                    notice_exists_both = Notice.objects.filter(project=project, notice_type='biocultural_and_traditional_knowledge').exists()
                    if not notice_exists_both:
                        notice_both = Notice.objects.create(project=project, notice_type='biocultural_and_traditional_knowledge', placed_by_researcher=researcher)
                        set_notice_defaults(notice_both)
                        notice.delete()
                else:
                    # If one notice was selected, check if it already exists
                    # If not, create new notice, delete old one
                    for selected in notices_selected:
                        if selected == 'bcnotice':
                            notice_exists_bc = Notice.objects.filter(project=project, notice_type='biocultural').exists()
                            if not notice_exists_bc:
                                bc_notice = Notice.objects.create(project=project, notice_type='biocultural', placed_by_researcher=researcher)
                                set_notice_defaults(bc_notice)
                                notice.delete()

                        elif selected == 'tknotice':
                            notice_exists_tk = Notice.objects.filter(project=project, notice_type='traditional_knowledge').exists()
                            if not notice_exists_tk:
                                tk_notice = Notice.objects.create(project=project, notice_type='traditional_knowledge', placed_by_researcher=researcher)
                                set_notice_defaults(tk_notice)
                                notice.delete()
            return redirect('researcher-projects', researcher.id)    

        context = {
            'researcher': researcher, 
            'project': project, 
            'notice': notice,
            'form': form, 
            'formset': formset,
            'contributors': contributors,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, proj_id):
    researcher = Researcher.objects.select_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels', 'project_status').get(id=proj_id)
        entities_notified = EntitiesNotified.objects.prefetch_related('communities').get(project=project)
        communities = Community.approved.prefetch_related('projects').all()

        if request.method == "POST":
            # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            communities_selected = request.POST.getlist('selected_communities')

            message = request.POST.get('notice_message')

            # Reference ID and title for notification
            reference_id = str(project.unique_id)
            title =  str(researcher.user.get_full_name()) + ' has notified you of a Project.'

            for community_id in communities_selected:
                # Add each selected community to notify entities instance
                community = Community.objects.get(id=community_id)
                entities_notified.communities.add(community)

                # Create project status, first comment and  notification
                ProjectStatus.objects.create(project=project, community=community, seen=False)
                ProjectComment.objects.create(project=project, community=community, sender=request.user, message=message)
                ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)
                entities_notified.save()
                
                # Create email
                send_email_notice_placed(project, community, researcher)
            
            return redirect('researcher-projects', researcher.id)

        context = {
            'researcher': researcher,
            'project': project,
            'communities': communities,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/notify.html', context)

def connections(request, pk):
    researcher = Researcher.objects.prefetch_related('projects').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        connections = Connections.objects.get(researcher=researcher)
        context = {
            'researcher': researcher,
            'connections': connections,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/connections.html', context)

def restricted_view(request, pk):
    researcher = Researcher.objects.prefetch_related('projects').get(id=pk)
    return render(request, 'researchers/restricted.html', {'researcher': researcher})