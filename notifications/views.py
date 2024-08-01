from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from notifications.models import ActionNotification, UserNotification


@login_required(login_url='login')
@csrf_exempt
def read_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return redirect('dashboard')


@login_required(login_url='login')
@csrf_exempt
def read_org_notification(request, pk):
    n = ActionNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return render(request, 'notifications/action-read.html')


@login_required(login_url='login')
def delete_user_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.delete()
    return redirect('dashboard')
