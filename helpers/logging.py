from datetime import datetime, timezone

from tklabels.models import TKLabel
from bclabels.models import BCLabel
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher


def get_current_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def get_log_data(instance):
    log_data = {
        'UTC-TIME': get_current_timestamp(),
        'RELATED-RESEARCHER': None,
        'RELATED-COMMUNITIES': [],
        'RELATED-INSTITUTIONS': [],
        'RELATED-TK-LABELS': [],
        'RELATED-BC-LABELS': [],
    }

    # get related researcher data of interest for this user
    if Researcher.objects.filter(user=instance).exists():
        researcher = Researcher.objects.get(user=instance)
        log_data['RELATED-RESEARCHER'] = {
            'id': researcher.id,
            'orcid': researcher.orcid,
            'contact_email': researcher.contact_email,
        }

    # get related community data of interest for this user
    for community in Community.objects.filter(community_creator=instance):
        log_data['RELATED-COMMUNITIES'].append(
            {
                'id': community.id,
                'name': community.community_name,
                'email': community.contact_email,
                'is_approved': community.is_approved,

            }
        )

    # get related institution data of interest for this user
    for institution in Institution.objects.filter(institution_creator=instance):
        log_data['RELATED-INSTITUTIONS'].append(
            {
                'id': institution.id,
                'name': institution.institution_name,
                'email': institution.contact_email,
                'is_approved': institution.is_approved,

            }
        )

    for bk in BCLabel.objects.filter(created_by=instance):
        log_data['RELATED-BC-LABELS'].append(
            {
                'id': bk.id,
                'name': bk.name,
                'unique_id': bk.unique_id,
                'is_approved': bk.is_approved,

            }
        )

    for tk in TKLabel.objects.filter(created_by=instance):
        log_data['RELATED-TK-LABELS'].append(
            {
                'id': tk.id,
                'name': tk.name,
                'unique_id': tk.unique_id,
                'is_approved': tk.is_approved,

            }
        )

    return log_data
