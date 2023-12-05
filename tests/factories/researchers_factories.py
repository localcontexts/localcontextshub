import factory
from django.core.files.base import ContentFile
from researchers.models import Researcher
from factories.accounts_factories import UserFactory
from faker import Faker

class ResearcherFactory(factory.django.DjangoModelFactory):
    '''This factory is for the Researcher model'''
    class Meta:
        model = Researcher
        skip_postgeneration_save=True

    user = factory.SubFactory(UserFactory)
    orcid = factory.Faker('isbn13')
    image = factory.LazyAttribute(lambda _: ContentFile(factory.django.ImageField()._make_data({'width': 1024, 'height': 768}), 'example.jpg'))
    contact_email = factory.Faker('email')
    contact_email_public = factory.Faker('boolean')
    description = factory.Faker('text', max_nb_chars=200)
    website = factory.Faker('url')
    primary_institution = factory.Faker('company')
    orcid_auth_token = factory.Faker('sha256')
    
    # @factory.post_generation
    # def set_many_to_many_fields(self, created, extracted, **kwargs):
    #     if created:
    #         self.save()