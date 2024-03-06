import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.conf import settings
from communities.models import InviteMember, Community
from notifications.models import UserNotification
from localcontexts.utils import dev_prod_or_local
from .downloads import download_otc_notice, download_cc_notices
import requests
from .models import NoticeDownloadTracker
from institutions.models import Institution
from researchers.models import Researcher

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

@login_required(login_url='login')
def download_institution_support_letter(request):
    try:
        url = f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/agreements/Local%20Contexts%20Institution%20Information%20and%20Support%20Letter%20Template.docx'
        response = requests.get(url)

        if response.status_code == 200:
            file_content = response.content
            response = HttpResponse(file_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename="LC_Institution_Support_Letter_Template.docx"'
            return response
    except:
        raise Http404()


@login_required(login_url='login')
def community_boundary_view(request, community_id):
    try:
        community = Community.objects.get(id=community_id)
        if not community.is_user_in_community(request.user):
            message = 'User Does Not Have Access To Community Boundary'
            print(f'{message}: {request.user}')
            raise Exception(message)

        boundary = []
        if community.boundary:
            boundary = community.boundary.get_coordinates(as_tuple=False)

        context = {
            'boundary': boundary
        }
        return render(request, 'boundary/boundary-view.html', context)
    except:
        raise Http404()


@login_required(login_url='login')
def boundary_view(request):
    try:
        boundary = request.GET.get('boundary')
        if boundary:
            boundary = json.loads(
                boundary.replace('(', '[').replace(')', ']')
            )
        else:
            boundary = []

        context = {
            'boundary': boundary
        }
        return render(request, 'boundary/boundary-view.html', context)
    except Exception as e:
        message = 'Invalid Boundary Format'
        print(f'{message}: {e}')
        raise Exception(message)
