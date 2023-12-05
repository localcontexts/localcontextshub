import factory
import factory.fuzzy
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory
from bclabels.models import BCLabel
import io
import os

class BCLabelFactory(factory.django.DjangoModelFactory):
    ''' This is the factory for the BCLabel model'''
    class Meta:
        model = BCLabel
        skip_postgeneration_save=True

    unique_id = factory.Faker('uuid4')
    version = factory.fuzzy.FuzzyInteger(1, 10)
    created_by = factory.SubFactory(UserFactory)
    label_type = factory.fuzzy.FuzzyChoice([choice[0] for choice in BCLabel.TYPES])
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
    audiofile = factory.django.FileField(
                filename='test_audio.mp3',
                data=io.BytesIO(os.urandom(1000)).read()
            )
    # @factory.post_generation
    # def set_many_to_many_fields(self, created, extracted, **kwargs):
    #     if created:
    #         self.save()
