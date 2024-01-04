from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.conf import settings
from communities.models import InviteMember
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
def boundaries_view(request):
    try:
        boundary = [
            (-76.677557, 36.629281), (-76.528485, 36.604392), (-76.454687, 36.635205), (-76.403028, 36.711),
            (-76.369081, 36.790268), (-76.324802, 36.888353), (-76.345465, 36.945019), (-76.425167, 36.979234),
            (-76.487158, 37.012255), (-76.537341, 37.027581), (-76.586048, 37.029939), (-76.631803, 37.011076),
            (-76.738072, 36.929676), (-76.795635, 36.890715), (-76.807442, 36.792633), (-76.814822, 36.714551),
            (-76.752832, 36.645868), (-76.677557, 36.629281)
        ]

        boundary = [[c[1], c[0]] for c in boundary]
        boundary2 = [[c[0]+.03, c[1]+.02] for c in boundary]

        context = {
            'boundaries': [boundary, boundary2]
        }
        return render(request, 'boundaries/boundaries-preview.html', context)
    except:
        raise Http404()
