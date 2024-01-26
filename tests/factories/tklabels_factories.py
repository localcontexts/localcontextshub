import factory
import factory.fuzzy
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory
from tklabels.models import TKLabel
import io
import os


class TKLabelFactory(factory.django.DjangoModelFactory):
    '''This factory is for the TKLabel model'''

    class Meta:
        model = TKLabel
        skip_postgeneration_save = True

    unique_id = factory.Faker('uuid4')
    version = factory.fuzzy.FuzzyInteger(1, 10)
    created_by = factory.SubFactory(UserFactory)
    label_type = factory.fuzzy.FuzzyChoice(
        [choice[0] for choice in TKLabel.TYPES])
    community = factory.SubFactory(CommunityFactory)
    name = factory.Faker('word')
    language_tag = factory.Faker('language_code')
    language = factory.Faker('language_name')
    label_text = factory.Faker('text')
    img_url = factory.Faker('image_url')
    svg_url = factory.Faker('image_url')
    is_approved = factory.Faker('boolean')
    approved_by = factory.SubFactory(UserFactory)
    last_edited_by = factory.SubFactory(UserFactory)
    created = factory.Faker('date_time_this_year')
    updated = factory.Faker('date_time_this_year')
    audiofile = factory.django.FileField(filename='test_audio.mp3',
                                         data=io.BytesIO(
                                             os.urandom(1000)).read())
