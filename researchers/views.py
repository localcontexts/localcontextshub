from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db import transaction
from django.db.models import Q
from itertools import chain

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from accounts.utils import get_users_name
from notifications.utils import send_action_notification_to_project_contribs

from communities.models import Community
from notifications.models import ActionNotification
from accounts.models import ServiceProviderConnections
from helpers.models import *
from projects.models import *
from api.models import AccountAPIKey

from projects.forms import *
from helpers.forms import ProjectCommentForm, OpenToCollaborateNoticeURLForm
from accounts.forms import (
    ContactOrganizationForm,
    SubscriptionForm,
)
from accounts.forms import ContactOrganizationForm
from api.forms import APIKeyGeneratorForm

from helpers.emails import *
from maintenance_mode.decorators import force_maintenance_mode_off

from .decorators import get_researcher
from .models import Researcher
from .forms import *
from .utils import *


@login_required(login_url='login')
def preparation_step(request):
    environment = dev_prod_or_local(request.get_host())
    researcher = True
    context = {
        'researcher': researcher,
        'environment': environment
    }
    return render(request, 'accounts/preparation.html', context)

@login_required(login_url='login')
def connect_researcher(request):
    researcher = is_user_researcher(request.user)
    form = ConnectResearcherForm(request.POST or None)
    user_form = form_initiation(request)
    
    env = dev_prod_or_local(request.get_host())
    
    if not researcher:
        if request.method == "POST":
            if form.is_valid() and user_form.is_valid() and  validate_recaptcha(request):
                mutable_post_data = request.POST.copy()
                subscription_data = {
                "first_name": user_form.cleaned_data['first_name'],
                "last_name": user_form.cleaned_data['last_name'],
                "email": request.user._wrapped.email,
                "inquiry_type": "Subscription",
                "account_type": "researcher_account",
                "organization_name": get_users_name(request.user),
                }
                mutable_post_data.update(subscription_data)
                subscription_form = SubscriptionForm(mutable_post_data)
                orcid_id = request.POST.get('orcidId')
                orcid_token = request.POST.get('orcidIdToken')

                if subscription_form.is_valid():
                    handle_researcher_creation(request, subscription_form, form, orcid_id, orcid_token, env)
                    return redirect('dashboard')
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Something went wrong. Please Try again later.",
                    )
                    return redirect('dashboard')
        context = {'form': form, 'env': env, 'user_form': user_form}
        return render(request, 'researchers/connect-researcher.html', context)
    else:
        return redirect('researcher-notices', researcher.id)

def public_researcher_view(request, pk):
    try:
        researcher = Researcher.objects.get(id=pk)

        # Do notices exist
        bcnotice = Notice.objects.filter(researcher=researcher, notice_type='biocultural').exists()
        tknotice = Notice.objects.filter(researcher=researcher, notice_type='traditional_knowledge').exists()
        attrnotice = Notice.objects.filter(researcher=researcher, notice_type='attribution_incomplete').exists()        
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher)

        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher created project ids
            researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').filter(unique_id__in=project_ids, project_privacy='Public').exclude(unique_id__in=archived).order_by('-date_modified')

        if request.user.is_authenticated:
            form = ContactOrganizationForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact researcher
                    if form.is_valid():
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = researcher.contact_email

                        send_contact_email(request, to_email, from_name, from_email, message, researcher)
                        messages.add_message(request, messages.SUCCESS, 'Message sent!')
                        return redirect('public-researcher', researcher.id)
                    else:
                        if not form.data['message']:
                            messages.add_message(request, messages.ERROR, 'Unable to send an empty message.')
                            return redirect('public-researcher', researcher.id)
                else:
                    messages.add_message(request, messages.ERROR, 'Something went wrong.')
                    return redirect('public-researcher', researcher.id)
        else:
            context = { 
                'researcher': researcher,
                'projects' : projects,
                'bcnotice': bcnotice,
                'tknotice': tknotice,
                'attrnotice': attrnotice,
                'otc_notices': otc_notices,
                'env': dev_prod_or_local(request.get_host()),
            }
            return render(request, 'public.html', context)

        context = { 
            'researcher': researcher,
            'projects' : projects,
            'bcnotice': bcnotice,
            'tknotice': tknotice,
            'attrnotice': attrnotice,
            'otc_notices': otc_notices,
            'form': form, 
            'env': dev_prod_or_local(request.get_host()),
        }
        return render(request, 'public.html', context)
    except:
        raise Http404()

@login_required(login_url='login')
def connect_orcid(request):
    researcher = Researcher.objects.get(user=request.user)
    return redirect('update-researcher', researcher.id)

@login_required(login_url='login')
def disconnect_orcid(request):
    researcher = Researcher.objects.get(user=request.user)
    researcher.orcid = ''
    researcher.orcid_auth_token = ''
    researcher.save()
    return redirect('update-researcher', researcher.id)


@login_required(login_url='login')
@get_researcher()
def update_researcher(request, researcher):
    env = dev_prod_or_local(request.get_host())

    if request.method == 'POST':
        update_form = UpdateResearcherForm(request.POST, request.FILES, instance=researcher)

        if 'clear_image' in request.POST:
            researcher.image = None
            researcher.save()
            return redirect('update-researcher', researcher.id)
        else:
            if update_form.is_valid():
                data = update_form.save(commit=False)
                data.save()

                if not researcher.orcid:
                    orcid_id = request.POST.get('orcidId')
                    orcid_token = request.POST.get('orcidIdToken')
                    researcher.orcid_auth_token = orcid_token
                    researcher.orcid = orcid_id
                    researcher.save()

                messages.add_message(request, messages.SUCCESS, 'Settings updated!')
                return redirect('update-researcher', researcher.id)
    else:
        update_form = UpdateResearcherForm(instance=researcher)

    context = {
        'update_form': update_form,
        'researcher': researcher,
        'user_can_view': True,
        'env': env
    }
    return render(request, 'account_settings_pages/_update-account.html', context)


@login_required(login_url='login')
@get_researcher(pk_arg_name='pk')
def researcher_notices(request, researcher):
    notify_restricted_message = False
    create_restricted_message = False

    try:
        subscription = Subscription.objects.get(researcher=researcher.id)
        not_approved_download_notice = None
        not_approved_shared_notice = None
    except Subscription.DoesNotExist:
        subscription = None
        not_approved_download_notice = "Your researcher account needs to be subscribed in order to download this Notice."
        not_approved_shared_notice = "Your researcher account needs to be subscribed in order to share this Notice."

    urls = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher).values_list('url', 'name', 'id')
    form = OpenToCollaborateNoticeURLForm(request.POST or None)

    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        is_sandbox = True
        otc_download_perm = 0
        download_notice_on_sandbox = "Download of Notices is not available on the sandbox site."
        share_notice_on_sandbox = "Sharing of Notices is not available on the sandbox site."
    else:
        is_sandbox = False
        otc_download_perm = 1 if researcher.is_subscribed else 0
        download_notice_on_sandbox = None
        share_notice_on_sandbox = None

    if request.method == 'POST':
        if form.is_valid():
            data = form.save(commit=False)
            data.researcher = researcher
            data.save()
            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Engagement Notice Added",
                project_id=data.id,
                action_account_type = 'researcher'
            )
        return redirect('researcher-notices', researcher.id)

    context = {
        'researcher': researcher,
        'user_can_view': True,
        'form': form,
        'urls': urls,
        'otc_download_perm': otc_download_perm,
        'notify_restricted_message': notify_restricted_message,
        'create_restricted_message': create_restricted_message,
        'is_sandbox': is_sandbox,
        'not_approved_download_notice': not_approved_download_notice,
        'download_notice_on_sandbox': download_notice_on_sandbox,
        'not_approved_shared_notice': not_approved_shared_notice,
        'share_notice_on_sandbox': share_notice_on_sandbox,
        'subscription': subscription,
    }
    return render(request, 'researchers/notices.html', context)


@login_required(login_url='login')
def delete_otc_notice(request, researcher_id, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect('researcher-notices', researcher_id)


@login_required(login_url='login')
@get_researcher(pk_arg_name='pk')
def researcher_projects(request, researcher):
    create_restricted_message = False
    try:
        subscription = Subscription.objects.get(researcher=researcher.id)
    except Subscription.DoesNotExist:
        subscription = None
    if not researcher.is_subscribed:
        create_restricted_message = 'The account must be subscribed before a Project can be created'

    bool_dict = {
        'has_labels': False,
        'has_notices': False,
        'created': False,
        'contributed': False,
        'is_archived': False,
        'title_az': False,
        'visibility_public': False,
        'visibility_contributor': False,
        'visibility_private': False,
        'date_modified': False
    }

    projects_list = list(chain(
        researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher projects
        researcher.researchers_notified.all().values_list('project__unique_id', flat=True), # projects researcher has been notified of
        researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
    ))
    project_ids = list(set(projects_list)) # remove duplicate ids
    archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
    projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_added')

    sort_by = request.GET.get('sort')

    if sort_by == 'all':
        return redirect('researcher-projects', researcher.id)

    elif sort_by == 'has_labels':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(tk_labels=None).order_by('-date_added')
        bool_dict['has_labels'] = True

    elif sort_by == 'has_notices':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None).exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['has_notices'] = True

    elif sort_by == 'created':
        created_projects = researcher.researcher_created_project.all().values_list('project__unique_id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=created_projects).exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['created'] = True

    elif sort_by == 'contributed':
        contrib = researcher.contributing_researchers.all().values_list('project__unique_id', flat=True)
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # check researcher created projects
            ProjectArchived.objects.filter(project_uuid__in=contrib, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=contrib).exclude(unique_id__in=project_ids).order_by('-date_added')
        bool_dict['contributed'] = True

    elif sort_by == 'archived':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived).order_by('-date_added')
        bool_dict['is_archived'] = True

    elif sort_by == 'title_az':
        projects = projects.order_by('title')
        bool_dict['title_az'] = True

    elif sort_by == 'archived':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived).order_by('-date_added')
        bool_dict['is_archived'] = True

    elif sort_by == 'visibility_public':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Public').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_public'] = True

    elif sort_by == 'visibility_contributor':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Contributor').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_contributor'] = True

    elif sort_by == 'visibility_private':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Private').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_private'] = True

    elif sort_by == 'date_modified':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_modified')
        bool_dict['date_modified'] = True

    page = paginate(request, projects, 10)

    results = []
    if request.method == 'GET':
        results = return_project_search_results(request, projects)

    context = {
        'projects': projects,
        'researcher': researcher,
        'user_can_view': True,
        'items': page,
        'results': results,
        'bool_dict': bool_dict,
        'create_restricted_message': create_restricted_message,
        'subscription': subscription,
    }
    return render(request, 'researchers/projects.html', context)


# Create Project
@login_required(login_url='login')
@get_researcher(pk_arg_name='pk')
def create_project(request, researcher, source_proj_uuid=None, related=None):
    name = get_users_name(request.user)
    notice_defaults = get_notice_defaults()
    notice_translations = get_notice_translations()

    if check_subscription(request, 'researcher', researcher.id) and dev_prod_or_local(request.get_host()) != 'SANDBOX':
        return redirect('researcher-projects', researcher.id)
    
    subscription = Subscription.objects.get(researcher=researcher)
    if request.method == "GET":
        form = CreateProjectForm(request.POST or None)
        formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
    elif request.method == "POST":
        form = CreateProjectForm(request.POST)
        formset = ProjectPersonFormset(request.POST)

        if form.is_valid() and formset.is_valid():
            data = form.save(commit=False)
            data.project_creator = request.user

            if subscription.project_count > 0:
                subscription.project_count -= 1
                subscription.save()
            # Define project_page field
            data.project_page = f'{request.scheme}://{request.get_host()}/projects/{data.unique_id}'

            # Handle multiple urls, save as array
            project_links = request.POST.getlist('project_urls')
            data.urls = project_links

            create_or_update_boundary(
                post_data=request.POST,
                entity=data
            )

            data.save()

            if source_proj_uuid and not related:
                data.source_project_uuid = source_proj_uuid
                data.save()
                ProjectActivity.objects.create(project=data, activity=f'Sub Project "{data.title}" was added to Project by {name} | Researcher')

            if source_proj_uuid and related:
                source = Project.objects.get(unique_id=source_proj_uuid)
                data.related_projects.add(source)
                source.related_projects.add(data)
                source.save()
                data.save()

                ProjectActivity.objects.create(project=data, activity=f'Project "{source.title}" was connected to Project by {name} | Researcher')
                ProjectActivity.objects.create(project=source, activity=f'Project "{data.title}" was connected to Project by {name} | Researcher')

            # Create activity
            ProjectActivity.objects.create(project=data, activity=f'Project was created by {name} | Researcher')

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Created",
                project_id=data.id,
                action_account_type = 'researcher'
            )

            # Add project to researcher projects
            creator = ProjectCreator.objects.select_related('researcher').get(project=data)
            creator.researcher = researcher
            creator.save()

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, researcher, data)

            # Create notices for project
            notices_selected = request.POST.getlist('checkbox-notice')
            translations_selected = request.POST.getlist('checkbox-translation')
            crud_notices(request, notices_selected, translations_selected, researcher, data, None, False)
            
            # Project person formset
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.name or instance.email:
                    instance.project = data
                    instance.save()
                # Send email to added person
                send_project_person_email(request, instance.email, data.unique_id, researcher)

            # Send notification
            title = 'Your project has been created, remember to notify a community of your project.'
            ActionNotification.objects.create(title=title, sender=request.user, notification_type='Projects', researcher=researcher, reference_id=data.unique_id)

            return redirect('researcher-projects', researcher.id)
    else:
        form = CreateProjectForm(None)
        formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())

    context = {
        'researcher': researcher,
        'notice_translations': notice_translations,
        'form': form,
        'formset': formset,
        'notice_defaults': notice_defaults,
        'user_can_view': True,
    }
    return render(request, 'researchers/create-project.html', context)


@login_required(login_url='login')
@get_researcher(pk_arg_name='pk')
def edit_project(request, researcher, project_uuid):
    project = Project.objects.get(unique_id=project_uuid)
    form = EditProjectForm(request.POST or None, instance=project)
    formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
    contributors = ProjectContributors.objects.get(project=project)
    notices = Notice.objects.none()
    notice_translations = get_notice_translations()
    notice_defaults = get_notice_defaults()

    # Check to see if notice exists for this project and pass to template
    if Notice.objects.filter(project=project).exists():
        notices = Notice.objects.filter(project=project, archived=False)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            has_changes = form.has_changed()
            data = form.save(commit=False)
            project_links = request.POST.getlist('project_urls')
            data.urls = project_links

            create_or_update_boundary(
                post_data=request.POST,
                entity=data
            )

            data.save()

            editor_name = get_users_name(request.user)
            ProjectActivity.objects.create(project=data, activity=f'Edits to Project were made by {editor_name}')

            communities = ProjectStatus.objects.filter( Q(status='pending') | Q(status__isnull=True),project=data, seen=True).select_related('community').order_by('community').distinct('community').values_list('community', flat=True)

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Edited",
                project_id=data.id,
                action_account_type = 'researcher'
            )

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.name or instance.email:
                    instance.project = project
                    instance.save()

            # Delete instances marked for deletion
            for instance in formset.deleted_objects:
                instance.delete()

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, researcher, data)

            # Which notices were selected to change
            notices_selected = request.POST.getlist('checkbox-notice')
            translations_selected = request.POST.getlist('checkbox-translation')
            has_changes = crud_notices(request, notices_selected, translations_selected, researcher, data, notices, has_changes)

            if has_changes:
                send_action_notification_project_status(request, project, communities)
        return redirect('researcher-project-actions', researcher.id, project.unique_id)

    context = {
        'researcher': researcher,
        'project': project,
        'notices': notices,
        'notice_defaults': notice_defaults,
        'form': form,
        'formset': formset,
        'contributors': contributors,
        'user_can_view': True,
        'urls': project.urls,
        'notice_translations': notice_translations,

    }
    return render(request, 'researchers/edit-project.html', context)


def project_actions(request, pk, project_uuid):
    try:
        project = Project.objects.prefetch_related(
            'bc_labels',
            'tk_labels',
            'bc_labels__community',
            'tk_labels__community',
            'bc_labels__bclabel_translation',
            'tk_labels__tklabel_translation',
        ).get(unique_id=project_uuid)

        if request.user.is_authenticated:
            researcher = Researcher.objects.get(id=pk)
            subscription = Subscription.objects.filter(researcher=pk).first()

            user_can_view = checkif_user_researcher(researcher, request.user)
            if not user_can_view or not project.can_user_access(request.user):
                return redirect('view-project', project.unique_id)
            else:
                notices = Notice.objects.filter(project=project, archived=False)
                creator = ProjectCreator.objects.get(project=project)
                statuses = ProjectStatus.objects.select_related('community').filter(project=project)
                comments = ProjectComment.objects.select_related('sender').filter(project=project)
                entities_notified = EntitiesNotified.objects.get(project=project)
                activities = ProjectActivity.objects.filter(project=project).order_by('-date')
                sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id',
                                                                                                         'title')
                name = get_users_name(request.user)
                label_groups = return_project_labels_by_community(project)
                can_download = False if dev_prod_or_local(request.get_host()) == 'SANDBOX' else True

                if not researcher.is_subscribed:
                    can_download = False

                # for related projects list
                project_ids = list(
                    set(researcher.researcher_created_project.all().values_list('project__unique_id', flat=True)
                        .union(researcher.researchers_notified.all().values_list('project__unique_id', flat=True))
                        .union(researcher.contributing_researchers.all().values_list('project__unique_id', flat=True))))
                project_ids_to_exclude_list = list(project.related_projects.all().values_list('unique_id',
                                                                                              flat=True))  # projects that are currently related
                # exclude projects that are already related
                project_ids = list(set(project_ids).difference(project_ids_to_exclude_list))
                projects_to_link = Project.objects.filter(unique_id__in=project_ids).exclude(
                    unique_id=project.unique_id).order_by('-date_added').values_list('unique_id', 'title')

                project_archived = False
                if ProjectArchived.objects.filter(project_uuid=project.unique_id, researcher_id=researcher.id).exists():
                    x = ProjectArchived.objects.get(project_uuid=project.unique_id, researcher_id=researcher.id)
                    project_archived = x.archived
                form = ProjectCommentForm(request.POST or None)

                communities_list = list(chain(
                    project.project_status.all().values_list('community__id', flat=True),
                ))

                if creator.community:
                    communities_list.append(creator.community.id)

                communities_ids = list(set(communities_list))  # remove duplicate ids
                communities = Community.approved.exclude(id__in=communities_ids).order_by('community_name')

                if request.method == 'POST':
                    if request.POST.get('message'):
                        if form.is_valid():
                            data = form.save(commit=False)
                            data.project = project
                            data.sender = request.user
                            data.sender_affiliation = 'Researcher'
                            data.save()
                            send_action_notification_to_project_contribs(project)
                            return redirect('researcher-project-actions', researcher.id, project.unique_id)

                    elif 'notify_btn' in request.POST:
                        # Set private project to contributor view
                        if project.project_privacy == 'Private':
                            project.project_privacy = 'Contributor'
                            project.save()

                        communities_selected = request.POST.getlist('selected_communities')
                        notification_count = subscription.notification_count
                        if notification_count == -1:
                            count = len(communities_selected)
                        else:
                            count = min(notification_count, len(communities_selected))

                        researcher_name = get_users_name(researcher.user)
                        title = f'{researcher_name} has notified you of a Project.'

                        for community_id in communities_selected[:count]:
                            # Add communities that were notified to entities_notified instance
                            community = Community.objects.get(id=community_id)
                            entities_notified.communities.add(community)

                            # Add activity
                            ProjectActivity.objects.create(project=project,
                                                           activity=f'{community.community_name} was notified by {name}')

                            # Adds activity to Hub Activity
                            HubActivity.objects.create(
                                action_user_id=request.user.id,
                                action_type="Community Notified",
                                community_id=community.id,
                                action_account_type='researcher',
                                project_id=project.id
                            )

                            # Create project status and  notification
                            ProjectStatus.objects.create(project=project, community=community,
                                                         seen=False)  # Creates a project status for each community
                            ActionNotification.objects.create(community=community, notification_type='Projects',
                                                              reference_id=str(project.unique_id), sender=request.user,
                                                              title=title)
                            entities_notified.save()

                            # Create email
                            send_email_notice_placed(request, project, community, researcher)
                        if subscription.notification_count > 0:
                            subscription.notification_count -= notification_count
                            subscription.save()
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)
                    elif 'link_projects_btn' in request.POST:
                        selected_projects = request.POST.getlist('projects_to_link')

                        activities = []
                        for uuid in selected_projects:
                            project_to_add = Project.objects.get(unique_id=uuid)
                            project.related_projects.add(project_to_add)
                            project_to_add.related_projects.add(project)
                            project_to_add.save()

                            activities.append(ProjectActivity(project=project,
                                                              activity=f'Project "{project_to_add.title}" was connected to Project by {name}'))
                            activities.append(ProjectActivity(project=project_to_add,
                                                              activity=f'Project "{project.title}" was connected to Project by {name}'))

                        ProjectActivity.objects.bulk_create(activities)
                        project.save()
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)

                    elif 'delete_project' in request.POST:
                        return redirect('researcher-delete-project', researcher.id, project.unique_id)

                    elif 'remove_contributor' in request.POST:
                        contribs = ProjectContributors.objects.get(project=project)
                        contribs.researchers.remove(researcher)
                        contribs.save()
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)

                context = {
                    'user_can_view': user_can_view,
                    'researcher': researcher,
                    'project': project,
                    'notices': notices,
                    'creator': creator,
                    'form': form,
                    'communities': communities,
                    'statuses': statuses,
                    'comments': comments,
                    'activities': activities,
                    'project_archived': project_archived,
                    'sub_projects': sub_projects,
                    'projects_to_link': projects_to_link,
                    'label_groups': label_groups,
                    'can_download': can_download,
                    'subscription': subscription,
                }
                return render(request, 'researchers/project-actions.html', context)
        else:
            return redirect('view-project', project.unique_id)
    except:
        raise Http404()

@login_required(login_url='login')
def archive_project(request, researcher_id, project_uuid):
    if not ProjectArchived.objects.filter(researcher_id=researcher_id, project_uuid=project_uuid).exists():
        ProjectArchived.objects.create(researcher_id=researcher_id, project_uuid=project_uuid, archived=True)
    else:
        archived_project = ProjectArchived.objects.get(researcher_id=researcher_id, project_uuid=project_uuid)
        if archived_project.archived:
            archived_project.archived = False
        else:
            archived_project.archived = True
        archived_project.save()
    return redirect('researcher-project-actions', researcher_id, project_uuid)


@login_required(login_url='login')
def delete_project(request, pk, project_uuid):
    project = Project.objects.get(unique_id=project_uuid)

    subscription = Subscription.objects.get(researcher=pk)
    if ActionNotification.objects.filter(reference_id=project.unique_id).exists():
        for notification in ActionNotification.objects.filter(reference_id=project.unique_id):
            notification.delete()
    
    project.delete()
    if subscription.project_count >= 0:
        subscription.project_count +=1
        subscription.save()
    return redirect('researcher-projects', pk)

@login_required(login_url='login')
def unlink_project(request, pk, target_proj_uuid, proj_to_remove_uuid):
    researcher = Researcher.objects.get(id=pk)
    target_project = Project.objects.get(unique_id=target_proj_uuid)
    project_to_remove = Project.objects.get(unique_id=proj_to_remove_uuid)
    target_project.related_projects.remove(project_to_remove)
    project_to_remove.related_projects.remove(target_project)
    target_project.save()
    project_to_remove.save()
    name = get_users_name(request.user)
    ProjectActivity.objects.create(project=project_to_remove, activity=f'Connection was removed between Project "{project_to_remove}" and Project "{target_project}" by {name}')
    ProjectActivity.objects.create(project=target_project, activity=f'Connection was removed between Project "{target_project}" and Project "{project_to_remove}" by {name}')
    return redirect('researcher-project-actions', researcher.id, target_project.unique_id)


@login_required(login_url='login')
@get_researcher(pk_arg_name='pk')
def connections(request, researcher):
    researchers = Researcher.objects.none()

    # Institution contributors
    institution_ids = researcher.contributing_researchers.exclude(
        institutions__id=None
    ).values_list('institutions__id', flat=True)
    institutions = (
        Institution.objects.select_related('institution_creator')
        .prefetch_related('admins', 'editors', 'viewers')
        .filter(id__in=institution_ids)
    )

    # Community contributors
    community_ids = researcher.contributing_researchers.exclude(
        communities__id=None
    ).values_list('communities__id', flat=True)
    communities = (
        Community.objects.select_related('community_creator')
        .prefetch_related("admins", "editors", "viewers")
        .filter(id__in=community_ids)
    )

    # Researcher contributors
    project_ids = researcher.contributing_researchers.values_list(
        "project__unique_id", flat=True
    )
    contributors = ProjectContributors.objects.filter(
        project__unique_id__in=project_ids
    ).values_list("researchers__id", flat=True)
    researchers = (
        Researcher.objects.select_related("user")
        .filter(id__in=contributors)
        .exclude(id=researcher.id)
    )

    context = {
        'researcher': researcher,
        'user_can_view': True,
        'communities': communities,
        'researchers': researchers,
        'institutions': institutions,
    }
    return render(request, 'researchers/connections.html', context)


@login_required(login_url="login")
@get_researcher(pk_arg_name='pk')
def connect_service_provider(request, researcher):
    try:
        if request.method == "GET":
            service_providers = ServiceProvider.objects.filter(is_certified=True)
            connected_service_providers = ServiceProviderConnections.objects.filter(
                researchers=researcher
            )

        elif request.method == "POST":
            if "connectServiceProvider" in request.POST:
                service_provider_id = request.POST.get('connectServiceProvider')
                connection_reference_id = f"{service_provider_id}:{researcher.id}_r"

                if ServiceProviderConnections.objects.filter(
                        service_provider=service_provider_id).exists():
                    # Connect researcher to existing Service Provider connection
                    sp_connection = ServiceProviderConnections.objects.get(
                        service_provider=service_provider_id
                    )
                    sp_connection.researchers.add(researcher)
                    sp_connection.save()
                else:
                    # Create new Service Provider Connection and add researcher
                    service_provider = ServiceProvider.objects.get(id=service_provider_id)
                    sp_connection = ServiceProviderConnections.objects.create(
                        service_provider = service_provider
                    )
                    sp_connection.researchers.add(researcher)
                    sp_connection.save()

                # Delete instances of disconnect Notifications
                if ActionNotification.objects.filter(
                    reference_id=connection_reference_id
                ).exists():
                    for notification in ActionNotification.objects.filter(
                        reference_id=connection_reference_id
                    ):
                        notification.delete()

                # Send notification of connection to Service Provider
                target_org = sp_connection.service_provider
                name = get_users_name(request.user)
                title = f"{name} has connected to {target_org.name}"
                send_simple_action_notification(
                    None, target_org, title, "Connections", connection_reference_id
                )

            elif "disconnectServiceProvider" in request.POST:
                service_provider_id = request.POST.get('disconnectServiceProvider')
                connection_reference_id = f"{service_provider_id}:{researcher.id}_r"

                sp_connection = ServiceProviderConnections.objects.get(
                    service_provider=service_provider_id
                )
                sp_connection.researchers.remove(researcher)
                sp_connection.save()

                # Delete instances of the connection notification
                if ActionNotification.objects.filter(
                    reference_id=connection_reference_id
                ).exists():
                    for notification in ActionNotification.objects.filter(
                        reference_id=connection_reference_id
                    ):
                        notification.delete()

                # Send notification of disconneciton to Service Provider
                target_org = sp_connection.service_provider
                name = get_users_name(request.user)
                title = f"{name} has been disconnected from {target_org.name}"
                send_simple_action_notification(
                    None, target_org, title, "Connections", connection_reference_id
                )

            # Set Show/Hide account in Service Provider connections
            elif request.POST.get('show_sp_connection') == None:
                researcher.show_sp_connection = False
                researcher.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Your preferences have been updated!'
                )

            elif request.POST.get('show_sp_connection') == 'on':
                researcher.show_sp_connection = True
                researcher.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Your preferences have been updated!'
                )

            return redirect("researcher-connect-service-provider", researcher.id)

        context = {
            'researcher': researcher,
            'user_can_view': True,
            'service_providers': service_providers,
            'connected_service_providers': connected_service_providers,
        }
        return render(request, 'account_settings_pages/_connect-service-provider.html', context)
    except:
        raise Http404()


@force_maintenance_mode_off
def embed_otc_notice(request, pk):
    layout = request.GET.get('lt')
    lang = request.GET.get('lang')
    align = request.GET.get('align')

    researcher = Researcher.objects.get(id=pk)
    otc_notices = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher)
    
    context = {
        'layout' : layout,
        'lang' : lang,
        'align' : align,
        'otc_notices' : otc_notices,
        'researcher' : researcher,
    }

    response = render(request, 'partials/_embed.html', context)
    response['Content-Security-Policy'] = 'frame-ancestors https://*'

    return response

# Create API Key
@login_required(login_url="login")
@get_researcher(pk_arg_name='pk')
@transaction.atomic
def api_keys(request, researcher, related=None):
    remaining_api_key_count = 0
    
    try:
        if researcher.is_subscribed:
                subscription = Subscription.objects.get(researcher=researcher)
                remaining_api_key_count = subscription.api_key_count
                
        if request.method == 'GET':
            form = APIKeyGeneratorForm(request.GET or None)
            account_keys = AccountAPIKey.objects.filter(researcher=researcher).values_list("prefix", "name", "encrypted_key")
    
        elif request.method == "POST":
            if "generate_api_key" in request.POST:
                if researcher.is_subscribed and subscription.api_key_count == 0:
                    messages.add_message(request, messages.ERROR, 'Your account has reached its API Key limit. '
                                        'Please upgrade your subscription plan to create more API Keys.')
                    return redirect("researcher-api-key", researcher.id)
                form = APIKeyGeneratorForm(request.POST)

                if researcher.is_subscribed:
                    if form.is_valid():
                        data = form.save(commit=False)
                        api_key, key = AccountAPIKey.objects.create_key(
                            name = data.name,
                            researcher_id = researcher.id
                        )
                        prefix = key.split(".")[0]
                        encrypted_key = urlsafe_base64_encode(force_bytes(key))
                        AccountAPIKey.objects.filter(prefix=prefix).update(encrypted_key=encrypted_key)

                        if subscription.api_key_count > 0:
                            subscription.api_key_count -= 1
                            subscription.save()
                    else:
                        messages.add_message(request, messages.ERROR, 'Please enter a valid API Key name.')
                        return redirect("researcher-api-key", researcher.id)
                
                else:
                    messages.add_message(request, messages.ERROR, 'Your account is not subscribed. '
                                        'You must have an active subscription to create more API Keys.')
                    return redirect("researcher-api-key", researcher.id)

                return redirect("researcher-api-key", researcher.id)
            
            elif "delete_api_key" in request.POST:
                prefix = request.POST['delete_api_key']
                api_key = AccountAPIKey.objects.filter(prefix=prefix)
                api_key.delete()

                if researcher.is_subscribed and subscription.api_key_count >= 0:
                    subscription.api_key_count +=1
                    subscription.save()

                return redirect("researcher-api-key", researcher.id)

        context = {
            "researcher" : researcher,
            "form" : form,
            "account_keys" : account_keys,
            "remaining_api_key_count" : remaining_api_key_count
        }
        return render(request, 'account_settings_pages/_api-keys.html', context)
    except:
        raise Http404()