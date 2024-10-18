from functools import wraps
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Community
from bclabels.utils import check_bclabel_type
from tklabels.utils import check_tklabel_type
from bclabels.forms import CustomizeBCLabelForm
from tklabels.forms import CustomizeTKLabelForm
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import HubActivity
from accounts.models import UserAffiliation
from django.db import transaction
from helpers.utils import handle_confirmation_and_subscription

def get_community(pk):
    return Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(
        id=pk)


def get_form_and_label_type(label_code):
    label_map = {
        'tk': (CustomizeTKLabelForm, "TK Label", check_tklabel_type(label_code)),
        'bc': (CustomizeBCLabelForm, "BC Label", check_bclabel_type(label_code))
    }
    return label_map.get(label_code[:2], (None, None, None))


def does_label_type_exist(community, label_code):
    tk_label_type = check_tklabel_type(label_code)
    bc_label_type = check_bclabel_type(label_code)

    if tk_label_type:
        return TKLabel.objects.filter(community=community, label_type=tk_label_type).exists()

    if bc_label_type:
        return BCLabel.objects.filter(community=community, label_type=bc_label_type).exists()

    return False


def has_new_community_id(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.session.get('new_community_id'):
            return render(request, '403.html', status=403)
        return function(request, *args, **kwargs)

    return wrap

def handle_community_creation(request, data, subscription_form, env):
    try:
        with transaction.atomic():
            data.save()
            handle_confirmation_and_subscription(request, subscription_form, data, env)
            # Add to user affiliations
            affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=request.user)
            affiliation.communities.add(data)
            affiliation.save()

            if env != 'SANDBOX':
                # Adds activity to Hub Activity
                HubActivity.objects.create(
                    action_user_id=request.user.id,
                    action_type="New Community",
                    community_id=data.id,
                    action_account_type='community'
                )
                request.session['new_community_id'] = data.id
            
    except Exception as e:
        messages.add_message(
            request,
            messages.ERROR,
            "An unexpected error has occurred here."
            " Please contact support@localcontexts.org.",
        )
        return redirect('dashboard')