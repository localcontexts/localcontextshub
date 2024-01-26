from django import template
from helpers.models import Notice
from projects.models import ProjectContributors, ProjectCreator

register = template.Library()

# @register.simple_tag
# def anchor(url_name, section_id, institution_id):
#     return reverse(url_name, kwargs={'pk': institution_id}) + f"#project-unique-{str(section_id)}"


@register.simple_tag
def get_notices_count(institution):
    return Notice.objects.filter(institution=institution,
                                 archived=False).count()


@register.simple_tag
def get_labels_count(institution):
    count = 0
    for instance in ProjectCreator.objects.select_related(
            'project').prefetch_related(
                'project__bc_labels',
                'project__tk_labels').filter(institution=institution):
        if instance.project.has_labels():
            count += 1

    return count


@register.simple_tag
def institution_contributing_projects(institution):
    return ProjectContributors.objects.select_related('project').filter(
        institutions=institution)


@register.simple_tag
def connections_count(institution):
    contributor_ids = institution.contributing_institutions.exclude(
        communities__id=None).values_list('communities__id', flat=True)
    return len(contributor_ids)
