from .models import Institution
from django.contrib import messages
from accounts.models import Subscription
from projects.models import Project

def get_institution(pk):
    return Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

# This is for retroactively adding ROR IDs to Institutions.
# Currently not being used anywhere.
def set_ror_id(institution):
    import requests

    url = 'https://api.ror.org/organizations'
    query = institution.institution_name
    params = { 'query': query }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            ror_id = data['items'][0]['id']
            institution.ror_id = ror_id
            institution.save()
        else:
            print('No matching institution found.')
    else:
        print('Error:', response.status_code)

def check_project_count(request, data, institution, project_count):
    if data.project_privacy in ('Public', 'Contributor') and project_count == 0:
        messages.add_message(request, messages.ERROR, 
                             'Your institution has reached its project limit.'
                             'Please upgrade your subscription plan to create more projects.')
        return False
    elif data.project_privacy == 'Private':
        private_project_count = Project.objects.filter(
            project_creator_project__institution=institution, 
            project_privacy='Private').count()
        if private_project_count >= 3:
            messages.add_message(request, messages.ERROR, 
                                 'Your institution has reached its private project limit. '
                                 'Please upgrade your subscription plan to create more projects.')
            return False
    return True

def can_change_project_privacy(request, old_project_privacy, new_privacy, institution):
    if old_project_privacy == 'Private' and new_privacy in ('Public', 'Contributor'):
        subscription = Subscription.objects.get(institution=institution)
        if subscription.project_count > 0:
            subscription.project_count -= 1
            subscription.save()
            #API Hit
            return True
        else:
            messages.add_message(request, messages.ERROR, 
                                        'Your institution has reached its project limit. Please upgrade your subscription plan to create more projects.')
            return False
    return True