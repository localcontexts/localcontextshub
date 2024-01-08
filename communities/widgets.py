from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe

from communities.models import Boundary


class BoundaryWidget(Widget):
    template_name = 'widget_forms/community/boundary_widget.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = None

    def render(self, name, value, attrs=None, renderer=None):
        boundaries = {}
        for boundary_id in self.attrs['boundary_ids']:
            boundaries[boundary_id] = Boundary.objects.get(id=boundary_id).get_coordinates()

        context = {'boundaries': boundaries, 'community_id': self.attrs['community_id']}
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
