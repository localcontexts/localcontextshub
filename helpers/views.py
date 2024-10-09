import json

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_sameorigin

from communities.models import InviteMember, Community
from notifications.models import UserNotification
from localcontexts.utils import dev_prod_or_local
from projects.models import Project
from .downloads import download_otc_notice, download_cc_notices
import requests
from .models import NoticeDownloadTracker
from institutions.models import Institution
from researchers.models import Researcher
from .utils import retrieve_native_land_all_slug_data


def restricted_view(request, exception=None):
    return render(request, '403.html', status=403)


@login_required(login_url='login')
def delete_member_invite(request, pk):
    invite = InviteMember.objects.get(id=pk)

    # Delete relevant UserNotification
    if UserNotification.objects.filter(to_user=invite.receiver, from_user=invite.sender, notification_type='invitation', reference_id=pk).exists():
        notification = UserNotification.objects.get(to_user=invite.receiver, notification_type='invitation', reference_id=pk)
        notification.delete()

    invite.delete()

    if '/communities/' in request.META.get('HTTP_REFERER'):
        return redirect('member-requests', invite.community.id)
    else:
        return redirect('institution-member-requests', invite.institution.id)


@login_required(login_url='login')
def download_open_collaborate_notice(request, perm, researcher_id=None, institution_id=None):
    # perm will be a 1 or 0
    has_permission = bool(perm)
    if dev_prod_or_local(request.get_host()) == 'SANDBOX' or not has_permission:
        return redirect('restricted')
    else:
        if researcher_id:
            researcher = get_object_or_404(Researcher, id=researcher_id)
            NoticeDownloadTracker.objects.create(researcher=researcher, user=request.user,open_to_collaborate_notice=True)

        elif institution_id:
            institution = get_object_or_404(Institution, id=institution_id)
            NoticeDownloadTracker.objects.create(institution=institution, user=request.user, open_to_collaborate_notice=True)

        return download_otc_notice(request)


@login_required(login_url='login')
def download_collections_care_notices(request, institution_id, perm):
    # perm will be a 1 or 0
    has_permission = bool(perm)
    if dev_prod_or_local(request.get_host()) == 'SANDBOX' or not has_permission:
        return redirect('restricted')
    else:
        NoticeDownloadTracker.objects.create(institution=Institution.objects.get(id=institution_id), user=request.user, collections_care_notices=True)
        return download_cc_notices(request)


@login_required(login_url='login')
def download_community_support_letter(request):
    try:
        url = f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/agreements/Local%20Contexts%20Community%20Support%20Letter%20Template.docx'
        response = requests.get(url)

        if response.status_code == 200:
            file_content = response.content
            response = HttpResponse(file_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename="LC_Community_Support_Letter_Template.docx"'
            return response
    except:
        raise Http404()


@xframe_options_sameorigin
def community_boundary_view(request, community_id):
    """
    Uses boundary in community for view
    """
    community = Community.objects.filter(id=community_id).first()
    if not community:
        message = 'Community Does Not Exist'
        raise Http404(message)

    boundary = []
    if community.boundary:
        boundary = community.boundary.get_coordinates(as_tuple=False)

    context = {
        'boundary': boundary
    }
    return render(request, 'boundary/boundary-preview.html', context)


@xframe_options_sameorigin
def project_boundary_view(request, project_id):
    """
    Uses boundary in project for view
    """
    project = Project.objects.filter(id=project_id).first()
    if not project:
        message = 'Project Does Not Exist'
        raise Http404(message)

    boundary = []
    if project.boundary:
        boundary = project.boundary.get_coordinates(as_tuple=False)

    context = {
        'boundary': boundary
    }
    return render(request, 'boundary/boundary-preview.html', context)


@login_required(login_url='login')
def boundary_preview(request):
    """
    Uses boundary in local storage for preview
    """
    context = {
        'preview_boundary': True,
    }
    return render(request, 'boundary/boundary-preview.html', context)


@login_required(login_url='login')
def native_land_data(request, slug):
    """
    Returns data associated with particular slug
    """
    # get all slug data from cache
    all_slug_data = cache.get('all_slug_data')

    # when cache doesn't exist, then retrieve actual data and cache it
    if all_slug_data is None:
        try:
            all_slug_data = retrieve_native_land_all_slug_data()
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ):
            return Http404('Unable to Retrieve All NLD Slug Data')
        cache.set('all_slug_data', all_slug_data)

    slug_data = all_slug_data.get(slug)
    if slug_data is None:
        return Http404(f'Unable to Retrieve Specific NLD Slug Data for {slug}')

    return JsonResponse(slug_data)
