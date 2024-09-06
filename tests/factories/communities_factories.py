import faker
import factory
from django.core.files.base import ContentFile
from communities.models import Community, InviteMember, JoinRequest, Boundary
from factories.accounts_factories import UserFactory
from factories.institutions_factories import InstitutionFactory

fake = faker.Faker()


class CommunityBoundaryFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the Community Model'''
    class Meta:
        model = Boundary
        skip_postgeneration_save = True

    coordinates = []


class CommunityFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the Community Model'''
    class Meta:
        model = Community
        skip_postgeneration_save = True

    boundary = factory.SubFactory(CommunityBoundaryFactory)
    community_creator = factory.SubFactory(UserFactory)
    community_name = factory.LazyAttribute(lambda x: fake.unique.company())
    community_entity = factory.Faker('company_suffix')
    contact_name = factory.Faker('name')
    contact_email = factory.Faker('email')
    image = factory.LazyAttribute(lambda _: ContentFile(factory.django.ImageField()._make_data({'width': 1024, 'height': 768}), 'example.png'))
    support_document = factory.django.FileField(filename='test.txt', content_type='text/plain', data=factory.Faker('text', max_nb_chars=100))
    description = factory.Faker('text', max_nb_chars=200)
    city_town = factory.Faker('city')
    state_province_region = factory.Faker('state')
    country = factory.Faker('country_code')
    website = factory.Faker('url')

    # Defining the RelatedFactoryList instances for editors, admins, and viewers to handle manytomanyfield
    admins = factory.RelatedFactoryList(UserFactory, size=2)
    editors = factory.RelatedFactoryList(UserFactory, size=1)
    viewers = factory.RelatedFactoryList(UserFactory, size=3)

    @factory.post_generation
    def set_many_to_many_fields(self, created, extracted, **kwargs):
        if created:
            # Set the admins field
            self.admins.set([self.community_creator])  # Add the community creator to admins

            # Set the editors field
            self.editors.set([UserFactory()])  # Create and add a new editor

            # Set the viewers field
            self.viewers.set([UserFactory()])   # Create and add a new viewers
            self.save()

    is_approved = factory.Faker('boolean')
    approved_by = factory.SubFactory(UserFactory)

class InviteMemberFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the InviteMember Model'''
    class Meta:
        model = InviteMember
        skip_postgeneration_save=True

    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    community = factory.SubFactory(CommunityFactory)
    institution = factory.SubFactory(InstitutionFactory)
    role = factory.Faker('random_element', elements=['admin', 'editor', 'viewer'])
    message = factory.Faker('text', max_nb_chars=200)
    status = factory.Faker('random_element', elements=['sent', 'accepted'])
    updated = factory.Faker('date_time_this_year')
    created = factory.Faker('date_time_this_year')

class JoinRequestFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the JoinRequest Model'''
    class Meta:
        model = JoinRequest
        skip_postgeneration_save=True

    user_from = factory.SubFactory(UserFactory)
    user_to = factory.SubFactory(UserFactory)
    role = factory.Faker('random_element', elements=['admin', 'editor', 'viewer'])
    community = factory.SubFactory(CommunityFactory)
    institution = factory.SubFactory(InstitutionFactory)
    message = factory.Faker('text', max_nb_chars=200)
    status = factory.Faker('random_element', elements=['sent', 'accepted'])
    date_sent = factory.Faker('date_time_this_year')