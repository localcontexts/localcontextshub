from django import template
from projects.models import ProjectContributors

register = template.Library()


@register.simple_tag
def institution_contributing_projects(institution):
    return ProjectContributors.objects.select_related('project').filter(institutions=institution)

