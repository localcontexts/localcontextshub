import factory
import factory.fuzzy
from projects.models import Project, ProjectArchived, ProjectPerson, ProjectNote, ProjectContributors, ProjectCreator, ProjectActivity
from factories.accounts_factories import UserFactory
from factories.tklabels_factories import TKLabelFactory
from factories.bclabels_factories import BCLabelFactory
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory
from factories.researchers_factories import ResearcherFactory


class ProjectArchivedFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectArchived Model'''

    class Meta:
        model = ProjectArchived
        skip_postgeneration_save = True

    project_uuid = factory.Faker('uuid4')
    community_id = factory.Faker('random_int', min=1, max=1000)
    institution_id = factory.Faker('random_int', min=1, max=1000)
    researcher_id = factory.Faker('random_int', min=1, max=1000)
    archived = factory.Faker('boolean')


class ProjectFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the Project Model'''

    class Meta:
        model = Project
        skip_postgeneration_save = True

    unique_id = factory.Faker('uuid4')
    project_creator = factory.SubFactory(UserFactory)
    project_page = factory.Faker('url')
    project_type = factory.fuzzy.FuzzyChoice(
        [choice[0] for choice in Project.TYPES])
    other_type = factory.Faker('text', max_nb_chars=60)
    project_privacy = factory.fuzzy.FuzzyChoice(
        [choice[0] for choice in Project.PRIVACY_LEVEL])
    title = factory.Faker('text', max_nb_chars=300)
    description = factory.Faker('paragraph')
    project_contact = factory.Faker('name')
    project_contact_email = factory.Faker('email')
    publication_doi = factory.Faker('text', max_nb_chars=200)
    project_data_guid = factory.Faker('text', max_nb_chars=200)
    providers_id = factory.Faker('text', max_nb_chars=200)
    project_boundary_geojson = factory.Faker('json')
    urls = factory.Faker('json')
    date_added = factory.Faker('date_time_this_year')
    date_modified = factory.Faker('date_time_this_year')
    source_project_uuid = factory.Faker('uuid4')
    bc_labels = factory.RelatedFactoryList(BCLabelFactory)
    tk_labels = factory.RelatedFactoryList(TKLabelFactory)

    #This is handling the manytomanyfield relation of model
    @factory.post_generation
    def set_many_to_many_fields(self, created, extracted, **kwargs):
        if created:
            # Set the BcLabel field
            self.bc_labels.set([BCLabelFactory()])

            # Set the Tklabel field
            self.tk_labels.set([TKLabelFactory()])
            self.save()


class ProjectPersonFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectPerson Model'''

    class Meta:
        model = ProjectPerson
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)
    name = factory.Faker('name')
    email = factory.Faker('email')


class ProjectNoteFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectNote Model'''

    class Meta:
        model = ProjectNote
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)
    community = factory.SubFactory(CommunityFactory)
    sender = factory.SubFactory(UserFactory)
    note = factory.Faker('text')
    created = factory.Faker('date_time_this_month')


class ProjectContributorsFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectContributors Model'''

    class Meta:
        model = ProjectContributors
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)
    institutions = factory.RelatedFactoryList(InstitutionFactory)
    communities = factory.RelatedFactoryList(CommunityFactory)
    researchers = factory.RelatedFactoryList(ResearcherFactory)

    #This function is handling the creation and assigning the manytomanyfield relations of model
    @factory.post_generation
    def set_many_to_many_fields(self, created, extracted, **kwargs):
        if created:
            existing_contributors = ProjectContributors.objects.filter()

            if existing_contributors.exists():
                # Reuse the existing instance
                self = existing_contributors.first()
            else:
                # Create and set the institutions ManyToMany field
                institutions = [InstitutionFactory() for _ in range(3)]
                self.institutions.set(institutions)

                # Set the communities ManyToMany field
                communities = [CommunityFactory() for _ in range(3)]
                self.communities.set(communities)

                # Set the researchers ManyToMany field
                researchers = [ResearcherFactory() for _ in range(3)]
                self.researchers.set(researchers)
            self.save()


class ProjectCreatorFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectCreator model'''

    class Meta:
        model = ProjectCreator
        skip_postgeneration_save = True

    community = factory.SubFactory(CommunityFactory)
    institution = factory.SubFactory(InstitutionFactory)
    researcher = factory.SubFactory(ResearcherFactory)
    project = factory.SubFactory(ProjectFactory)


class ProjectActivityFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectActivity Model'''

    class Meta:
        model = ProjectActivity
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)
    date = factory.Faker('date_time_this_month')
    activity = factory.Faker('text')
