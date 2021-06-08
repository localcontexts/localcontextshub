import uuid
from django.db import models
from django.contrib.auth.models import User
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher

class Project(models.Model):
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Sample', 'Sample'),
    )
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    project_creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_creator")
    project_type = models.CharField(max_length=20, null=True, choices=TYPES)
    title = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)
    project_image = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    project_contact = models.CharField(max_length=100, null=True)
    project_contact_email = models.EmailField(max_length=100, null=True)
    publication_doi = models.CharField(max_length=200, blank=True, null=True)
    project_data_guid = models.CharField(max_length=200, blank=True, null=True)
    recommended_citation = models.TextField(null=True, blank=True)
    geome_project_id = models.IntegerField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    publication_date = models.DateField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    is_public = models.BooleanField(default=True, null=True)
    bclabels = models.ManyToManyField("bclabels.BCLabel", verbose_name="BC Labels", blank=True, related_name="project_labels")
    tklabels = models.ManyToManyField("tklabels.TKLabel", verbose_name="TK Labels", blank=True, related_name="project_tklabels")

    def has_labels(self):
        bc_labels = self.bclabels.count()
        tk_labels = self.tklabels.count()
        if bc_labels + tk_labels > 0:
            return True
        else:
            return False

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ('-date_added',)

class ProjectContributors(models.Model):
    project = models.OneToOneField(Project, related_name="project_contributors", null=True, on_delete=models.CASCADE)
    # institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.SET_NULL)
    # community = models.ForeignKey(Community, null=True, blank=True, on_delete=models.SET_NULL)
    # researcher = models.ForeignKey(Researcher, null=True, blank=True, on_delete=models.SET_NULL)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="contributing_institutions")
    communities = models.ManyToManyField(Community, blank=True, related_name="contributing_communities")
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="contributing_researchers")


    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'Project Contributors'
        verbose_name_plural = 'Project Contributors'


