from django import template
from projects.models import ProjectContributors

register = template.Library()


@register.simple_tag
def researcher_contributing_projects(researcher):
    return ProjectContributors.objects.select_related('project').filter(researchers=researcher)
