import factory
from django.core.files.base import ContentFile
from django_countries.fields import Country
from institutions.models import Institution
from factories.accounts_factories import UserFactory

class InstitutionFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the Institution Model'''
    class Meta:
        model = Institution
        skip_postgeneration_save=True

    institution_creator = factory.SubFactory(UserFactory)
    institution_name = factory.Faker('company')
    contact_name = factory.Faker('name')
    contact_email = factory.Faker('email')
    image = factory.LazyAttribute(lambda _: ContentFile(factory.django.ImageField()._make_data({'width': 1024, 'height': 768}), 'example.jpg'))
    description = factory.Faker('text', max_nb_chars=200)
    ror_id = factory.Faker('uuid4')
    city_town = factory.Faker('city')
    state_province_region = factory.Faker('state')
    country = factory.Faker('country_code')
    website = factory.Faker('url')
    is_ror = factory.Faker('boolean')