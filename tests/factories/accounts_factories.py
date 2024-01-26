import factory
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from accounts.models import Profile
import faker

fake = faker.Faker()
username_counter = 0


class UserFactory(factory.django.DjangoModelFactory):
    '''This factory is for the User Model used in profile model.'''

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.LazyAttribute(lambda x: fake.user_name())
    email = factory.LazyAttribute(lambda x: fake.email())
    password = factory.LazyAttribute(lambda x: fake.password(length=10))

    @factory.post_generation
    def set_username(self, create, extracted, **kwargs):
        global username_counter
        if create:
            username_counter += 1
            self.username = f"user_{username_counter}"
            self.save()


class ProfileFactory(factory.django.DjangoModelFactory):
    '''This factory is for the Profile Model '''

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    profile_pic = factory.LazyAttribute(lambda _: ContentFile(
        factory.django.ImageField()._make_data({
            'width': 1024,
            'height': 768
        }), 'example.jpg'))
    city_town = factory.Faker('city')
    state_province_region = factory.Faker('state')
    country = factory.Faker('country_code')
    position = factory.Faker('job')
    affiliation = factory.Faker('company')
    preferred_language = factory.Faker('language_name')
    api_key = factory.Faker('sha256')
    languages_spoken = fake.language_name()
    is_researcher = factory.Faker('boolean')
    onboarding_on = factory.Faker('boolean')
