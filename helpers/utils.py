import json
import urllib
import zipfile
from typing import Union

import requests
from django.conf import settings
from django.template.loader import get_template
from io import BytesIO
from accounts.models import UserAffiliation
from tklabels.models import TKLabel
from bclabels.models import BCLabel
from helpers.models import LabelTranslation, LabelVersion, LabelTranslationVersion, HubActivity
from xhtml2pdf import pisa

from communities.models import Community, JoinRequest, InviteMember, Boundary
from institutions.models import Institution
from researchers.models import Researcher
from .models import Notice
from notifications.models import *

from accounts.utils import get_users_name
from notifications.utils import send_user_notification_member_invite_accept
from helpers.emails import send_membership_email
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404


def check_member_role(user, organization):
    # Check for creator roles
    if isinstance(organization, Community) and user == organization.community_creator:
        return 'admin'
    if isinstance(organization, Institution) and user == organization.institution_creator:
        return 'admin'

    # Check for admin/editor/viewer roles
    if organization.admins.filter(id=user.id).exists():
        return 'admin'
    elif organization.editors.filter(id=user.id).exists():
        return 'editor'
    elif organization.viewers.filter(id=user.id).exists():
        return 'viewer'

    return False


def change_member_role(org, member, current_role, new_role):
    role_map = {
        'admin': org.admins,
        'editor': org.editors,
        'viewer': org.viewers,
    }

    if current_role and current_role in role_map:
        role_map[current_role].remove(member)
    
    if new_role and new_role in role_map:
        role_map[new_role].add(member)

    org.save()


def add_user_to_role(account, role, user):
    role_map = {
        'admin': account.admins,
        'editor': account.editors,
        'viewer': account.viewers,
    }
    role_map[role].add(user)
    account.save()
    
    
def accept_member_invite(request, invite_id):
    invite = get_object_or_404(InviteMember, id=invite_id)
    affiliation = get_object_or_404(UserAffiliation, user=invite.receiver)

    # Which organization, add to user affiliation
    account = invite.community or invite.institution
    if invite.community:
        affiliation.communities.add(account)
    if invite.institution:
        affiliation.institutions.add(account)
    
    affiliation.save()
    
    add_user_to_role(account, invite.role, invite.receiver) # Add user to role
    send_user_notification_member_invite_accept(invite) # Send UserNotifications
    send_membership_email(request, account, invite.receiver, invite.role) # Send email notifications letting user know they are a member

    # Delete relevant user notification
    UserNotification.objects.filter(to_user=invite.receiver, from_user=invite.sender, reference_id=invite.id).delete()


def accepted_join_request(request, org, join_request_id, selected_role):
    # Passes instance of Community or Institution, a join_request pk, and a selected role
    if JoinRequest.objects.filter(id=join_request_id).exists():
        join_request = JoinRequest.objects.get(id=join_request_id)
        if selected_role is None:
            pass
        else:
            # Add organization to userAffiliation and delete relevant action notification
            affiliation = UserAffiliation.objects.get(user=join_request.user_from)
            if isinstance(org, Community):
                affiliation.communities.add(org)
                if ActionNotification.objects.filter(sender=join_request.user_from, community=org, reference_id=join_request.id).exists():
                    notification = ActionNotification.objects.get(sender=join_request.user_from, community=org, reference_id=join_request.id)
                    notification.delete()
            if isinstance(org, Institution):
                affiliation.institutions.add(org)
                if ActionNotification.objects.filter(sender=join_request.user_from, institution=org, reference_id=join_request.id).exists():
                    notification = ActionNotification.objects.get(sender=join_request.user_from, institution=org, reference_id=join_request.id)
                    notification.delete()

            # Add member to role
            if selected_role == 'Administrator':
                org.admins.add(join_request.user_from)
            elif selected_role == 'Editor':
                org.editors.add(join_request.user_from)
            elif selected_role == 'Viewer':
                org.viewers.add(join_request.user_from)
            
            # Create UserNotification
            sender = join_request.user_from
            title = f"You are now a member of {org}!"
            UserNotification.objects.create(to_user=sender, title=title, notification_type="Accept")

            send_membership_email(request, org, sender, selected_role)

            # Delete join request
            join_request.delete()

# h/t: https://stackoverflow.com/questions/59695870/generate-multiple-pdfs-and-zip-them-for-download-all-in-a-single-view
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    p = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
    pdf = buffer.getvalue()
    buffer.close()
    if not p.err:
        return pdf
    return None

def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])

    return mem_zip.getvalue()

def get_labels_json():
    json_data = open('./localcontexts/static/json/Labels.json')
    data = json.load(json_data) #deserialize
    return data

def get_notice_translations():
    json_path = finders.find('json/NoticeTranslations.json')
    with open(json_path, 'r', encoding="utf8") as file:
        data = json.load(file)
    
    # Restructure the data as a nested dictionary with noticeType and language as keys
    notice_translations = {}
    for item in data:
        notice_type = item['noticeType']
        language_tag = item['languageTag']
        if notice_type not in notice_translations:
            notice_translations[notice_type] = {}
        notice_translations[notice_type][language_tag] = item
    return notice_translations

def get_notice_defaults():
    json_path = finders.find('json/Notices.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

# Create/Update/Delete Notices and Notice Translations
def crud_notices(request, selected_notices, selected_translations, organization, project, existing_notices, has_changes):
    # organization: instance of institution or researcher
    # selected_notices: list: ['attribution_incomplete', 'bcnotice', 'tknotice']
    # existing_notices: a queryset of notices that exist for this project already
    # selected_translations: list: ['traditional_knowledge-fr', 'biocultural-es'], etc.

    from projects.models import ProjectActivity
    name = get_users_name(request.user)

    def create(notice_type):
        if isinstance(organization, (Institution, Researcher)):
            notice_fields = {
                'notice_type': notice_type,
                'project': project,
            }

            if isinstance(organization, Institution):
                notice_fields['institution'] = organization
                # Adds activity to Hub Activity
                HubActivity.objects.create(
                    action_user_id=request.user.id,
                    action_type="Disclosure Notice(s) Added",
                    project_id=project.id,
                    action_account_type = 'institution',
                    institution_id=organization.id
                )
            elif isinstance(organization, Researcher):
                notice_fields['researcher'] = organization
                # Adds activity to Hub Activity
                HubActivity.objects.create(
                    action_user_id=request.user.id,
                    action_type="Disclosure Notice(s) Added",
                    project_id=project.id,
                    action_account_type = 'researcher'
                )

            new_notice = Notice.objects.create(**notice_fields)
            ProjectActivity.objects.create(project=project, activity=f'{new_notice.name} was applied to the Project by {name}')

            # Create any notice translations
            update_notice_translation(new_notice, selected_translations)

    def create_notices(existing_notice_types):
        nonlocal has_changes
        for notice_type in selected_notices:
            if notice_type:
                if existing_notice_types:
                    if not notice_type in existing_notice_types:
                        has_changes = True
                        create(notice_type)
                else:
                    create(notice_type)
    
    def update_notice_translation(notice, selected_translations):
        selected_notice_types_langs = [value.split('-') for value in selected_translations]
        nonlocal has_changes

        for translation in notice.notice_translations.all():
            ntype = translation.notice_type
            lang_tag = translation.language_tag

            # If this notice translation is not in the selected translations and its type matches the notice, delete it
            if [ntype, lang_tag] not in selected_notice_types_langs and notice.notice_type == ntype:
                has_changes = True
                translation.delete()

        for ntype, lang_tag in selected_notice_types_langs:
            # Check if the notice type matches the selected translation
            if notice.notice_type == ntype:
                # If translation of this type in this language does NOT exist, create it.
                if not notice.notice_translations.filter(notice_type=ntype, language_tag=lang_tag).exists():
                    has_changes = True
                    notice.save(language_tag=lang_tag)
                
    if existing_notices:
        existing_notice_types = []
        for notice in existing_notices:
            existing_notice_types.append(notice.notice_type)
            if not notice.notice_type in selected_notices: # if existing notice not in selected notices, delete notice
                has_changes = True
                notice.delete()
                ProjectActivity.objects.create(project=project, activity=f'{notice.name} was removed from the Project by {name}')
            update_notice_translation(notice, selected_translations)
        create_notices(existing_notice_types)
        return has_changes
    else:
        create_notices(None)
        return has_changes

def add_remove_labels(request, project, community):
    from projects.models import ProjectActivity
    # Get uuids of each label that was checked and add them to the project
    bclabels_selected = request.POST.getlist('selected_bclabels')
    tklabels_selected = request.POST.getlist('selected_tklabels')

    bclabels = BCLabel.objects.filter(unique_id__in=bclabels_selected)
    tklabels = TKLabel.objects.filter(unique_id__in=tklabels_selected)

    user = get_users_name(request.user)

    # find target community labels and clear those only!
    if project.bc_labels.filter(community=community).exists():

        for bclabel in project.bc_labels.filter(community=community).exclude(unique_id__in=bclabels_selected): # does project have labels from this community that aren't the selected ones?
            project.bc_labels.remove(bclabel) 
            ProjectActivity.objects.create(project=project, activity=f'{bclabel.name} Label was removed by {user} | {community.community_name}')

    if project.tk_labels.filter(community=community).exists():
        for tklabel in project.tk_labels.filter(community=community).exclude(unique_id__in=tklabels_selected):
            project.tk_labels.remove(tklabel)
            ProjectActivity.objects.create(project=project, activity=f'{tklabel.name} Label was removed by {user} | {community.community_name}')

    for bclabel in bclabels:
        if not bclabel in project.bc_labels.all(): # if label not in project labels, apply it
            project.bc_labels.add(bclabel)
            ProjectActivity.objects.create(project=project, activity=f'{bclabel.name} Label was applied by {user} | {community.community_name}')

    for tklabel in tklabels:
        if not tklabel in project.tk_labels.all():
            project.tk_labels.add(tklabel)
            ProjectActivity.objects.create(project=project, activity=f'{tklabel.name} Label was applied by {user} | {community.community_name}')
    
    project.save()


def handle_label_versions(label):
    # passes instance of BCLabel or TKLabel
    version = LabelVersion.objects.none()
    translations = LabelTranslation.objects.none()
    version_num = 0

    if isinstance(label, BCLabel):
        translations = LabelTranslation.objects.filter(bclabel=label)

        # If approved version exists, set version number to 1 more than the latest
        latest_version = LabelVersion.objects.filter(bclabel=label).order_by('-version').first()

        if latest_version is not None:
            if latest_version.is_approved:
                version_num = latest_version.version + 1
            elif not latest_version.is_approved:
                latest_version.is_approved = True
                latest_version.save()
        else:
            version_num = 1
            label.version = 1
            label.save()

        # Create Version for BC Label
        version = LabelVersion.objects.create(
            bclabel=label,
            version=version_num, 
            created_by=label.created_by, 
            is_approved=True,
            approved_by=label.approved_by,
            version_text=label.label_text,
            created=label.created
        )

    if isinstance(label, TKLabel):
        translations = LabelTranslation.objects.filter(tklabel=label)

        # If approved version exists, set version number to 1 more than the latest
        latest_version = LabelVersion.objects.filter(tklabel=label).order_by('-version').first()

        if latest_version is not None:
            if latest_version.is_approved:
                version_num = latest_version.version + 1
            elif not latest_version.is_approved:
                latest_version.is_approved = True
                latest_version.save()
        else:
            version_num = 1
            label.version = 1
            label.save()

        # Create Version for TK Label
        version = LabelVersion.objects.create(
            tklabel=label,
            version=version_num, 
            created_by=label.created_by, 
            is_approved=True,
            approved_by=label.approved_by,
            version_text=label.label_text,
            created=label.created
        )

    # Create version translations
    for t in translations:
        LabelTranslationVersion.objects.create(
            version_instance=version,
            translated_name=t.translated_name,
            language=t.language, 
            language_tag=t.language_tag,
            translated_text=t.translated_text,
            created=version.created
        )

def discoverable_project_view(project, user):
    project_contributors = project.project_contributors
    creator_account = project.project_creator_project.first()
    is_created_by = creator_account.which_account_type_created()
    notified = project.project_notified.first()

    discoverable = 'partial'

    if not user.is_authenticated:
        discoverable = 'partial'
    elif creator_account.is_user_in_creator_account(user, is_created_by):
        discoverable = True
    elif project_contributors.is_user_contributor(user):
        discoverable = True
    elif notified.is_user_in_notified_account(user):
        discoverable = True
    else:
        discoverable = False

    return discoverable

def get_alt_text(data, bclabels, tklabels):
    for label in bclabels:
        item = next((x for x in data['bcLabels'] if x['labelName'] == label.name), None)
        if item is not None:
            label.alt_text = item['labelAlternateText']
        else:
            label.alt_text = "BC label icon"  
    
    for label in tklabels:
        item = next((x for x in data['tkLabels'] if x['labelName'] == label.name), None)
        if item is not None:
            label.alt_text = item['labelAlternateText']
        else:
            label.alt_text = "TK label icon" 
    
    return bclabels, tklabels  

def validate_email(email):
    url = f"{settings.MAILGUN_V4_BASE_URL}/address/validate"
    auth = ("api", settings.MAILGUN_API_KEY)
    params = {"address": email}
    
    response = requests.get(url, auth=auth, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("result") == "deliverable":
            return True
        else:
            return False
    else:
        print("Request failed with status code:", response.status_code)
        return False

def validate_recaptcha(request_object):
    recaptcha_response = request_object.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    return result.get('success', False) and result.get('score', 0.0) >= settings.RECAPTCHA_REQUIRED_SCORE


def create_or_update_boundary(post_data: dict, entity: Union['Community', 'Project']):
    entity.share_boundary_publicly = post_data.get('share-boundary-publicly') == 'on'
    raw_boundary_payload = post_data.get('boundary-payload')

    if raw_boundary_payload in ['', None]:
        return

    data = json.loads(raw_boundary_payload)
    name = data.get('name')
    source = data.get('source')
    boundary_data = data.get('boundary')

    if name:
        entity.name_of_boundary = name

    if source:
        entity.source_of_boundary = source

    boundary_coordinates = boundary_data if boundary_data else []
    if entity.boundary:
        # update boundary when it exists
        entity.boundary.coordinates = boundary_coordinates
    else:
        # create boundary when it does not exist
        entity.boundary = Boundary(coordinates=boundary_coordinates)
    entity.boundary.save()
