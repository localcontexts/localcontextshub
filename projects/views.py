from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from projects.models import Boundary
from helpers.exceptions import UnconfirmedAccountException
from .models import Project, ProjectContributors, ProjectCreator
from helpers.models import Notice
from django.http import Http404
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from django.http import Http404, HttpResponse
from accounts.models import UserAffiliation
from researchers.models import Researcher
from helpers.downloads import download_project_zip
from localcontexts.utils import dev_prod_or_local
from .utils import can_download_project, return_project_labels_by_community

from maintenance_mode.decorators import force_maintenance_mode_off

@force_maintenance_mode_off
def view_project(request, unique_id):
    try:
        project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=unique_id)
        creator = ProjectCreator.objects.get(project=project)
        status = creator.account_is_confirmed()
        creator.validate_user_access(request.user)
    except (Project.DoesNotExist, UnconfirmedAccountException):
        return render(request, '404.html', status=404)

    sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id', 'title')
    notices = Notice.objects.filter(project=project, archived=False).exclude(notice_type='open_to_collaborate')

    communities = None
    institutions = None
    user_researcher = Researcher.objects.none()
    label_groups = return_project_labels_by_community(project)
    can_download = can_download_project(request, creator)
    #  If user is logged in AND belongs to account of a contributor
    if request.user.is_authenticated:
        affiliations = UserAffiliation.objects.get(user=request.user)

        community_ids = ProjectContributors.objects.filter(project=project).values_list('communities__id', flat=True)
        institution_ids = ProjectContributors.objects.filter(project=project).values_list('institutions__id', flat=True)
        communities = affiliations.communities.filter(id__in=community_ids)
        institutions = affiliations.institutions.filter(id__in=institution_ids)

        researcher_ids = ProjectContributors.objects.filter(project=project).values_list('researchers__id', flat=True)

        if Researcher.objects.filter(user=request.user).exists():
            researcher = Researcher.objects.get(user=request.user)
            researchers = Researcher.objects.filter(id__in=researcher_ids)
            if researcher in researchers:
                user_researcher = Researcher.objects.get(id=researcher.id)
    
    template_name = project.get_template_name(request.user)
            
    context = {
        'project': project, 
        'notices': notices,
        'creator': creator,
        'communities': communities,
        'institutions': institutions,
        'user_researcher': user_researcher,
        'sub_projects': sub_projects,
        'template_name': template_name,
        'can_download': can_download,
        'label_groups': label_groups,
        'status': status,
    }

    if template_name:
        if project.can_user_access(request.user) == 'partial' or project.can_user_access(request.user) == True:
            return render(request, 'projects/view-project.html', context)
        else:
            return redirect('restricted')
    else:
        return redirect('restricted')


def download_project(request, unique_id):
    try:
        project = Project.objects.get(unique_id=unique_id)
        can_download = can_download_project(request, project.project_creator_project.first())

        if project.project_privacy == "Private" or dev_prod_or_local(request.get_host()) == 'SANDBOX' or not can_download:
            return redirect('restricted')
        else:
            return download_project_zip(project)
    except:
        raise Http404()

@force_maintenance_mode_off
def embed_project(request, unique_id):
    layout = request.GET.get('lt')
    lang = request.GET.get('lang')
    align = request.GET.get('align')

    project = project = Project.objects.prefetch_related(
                    'bc_labels', 
                    'tk_labels', 
                    'bc_labels__community', 
                    'tk_labels__community',
                    'bc_labels__bclabel_translation', 
                    'tk_labels__tklabel_translation',
                    ).get(unique_id=unique_id)
    notices = Notice.objects.filter(project=project, archived=False)
    label_groups = return_project_labels_by_community(project)

    if project.project_privacy == "Public":
        context = {
            'layout' : layout,
            'lang' : lang,
            'align' : align,
            'notices' : notices,
            'label_groups' :  label_groups,
            'project' : project,
            'restricted': False,
        }
    
    else:
        context = {
            'restricted': True,
        }

    response = render(request, 'partials/_embed.html', context)
    response['Content-Security-Policy'] = 'frame-ancestors https://*'

    return response


@login_required(login_url='login')
def reset_project_boundary(request, pk):
    try:
        project = Project.objects.get(id=pk)
        creator = ProjectCreator.objects.get(project=project)
        creator.validate_user_access(request.user)

        project.name_of_boundary = ''
        project.source_of_boundary = ''

        if project.boundary:
            # update boundary when it exists
            project.boundary.coordinates = []
            project.boundary.save()
        else:
            # create boundary when it does not exist
            project.boundary = Boundary(coordinates=[])

        project.save()
        return HttpResponse(status=204)
    except (Project.DoesNotExist, UnconfirmedAccountException):
        return render(request, '404.html', status=404)
