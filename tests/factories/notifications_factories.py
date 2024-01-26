import factory
import factory.fuzzy
from faker import Faker
from notifications.models import UserNotification, ActionNotification
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory, InstitutionFactory
from factories.researchers_factories import ResearcherFactory

faker = Faker()


class UserNotificationFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the UserNotification Model'''

    class Meta:
        model = UserNotification
        skip_postgeneration_save = True

    title = factory.LazyAttribute(lambda n: faker.sentence()[:200])
    message = factory.Faker('text')
    to_user = factory.SubFactory(UserFactory)
    from_user = factory.SubFactory(UserFactory)
    notification_type = factory.fuzzy.FuzzyChoice(
        choices=[choice[0] for choice in UserNotification.TYPES])
    community = factory.SubFactory(CommunityFactory)
    institution = factory.SubFactory(InstitutionFactory)
    role = factory.fuzzy.FuzzyChoice(
        choices=[choice[0] for choice in UserNotification.ROLES])
    reference_id = factory.LazyAttribute(lambda n: faker.uuid4()[:20])
    viewed = factory.Faker('boolean')
    created = factory.Faker('date_time_this_year')


class ActionNotificationFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ActionNotification Model'''

    class Meta:
        model = ActionNotification
        skip_postgeneration_save = True

    title = factory.LazyAttribute(lambda n: faker.sentence()[:200])
    notification_type = factory.fuzzy.FuzzyChoice(
        choices=[choice[0] for choice in ActionNotification.TYPES])
    sender = factory.SubFactory(UserFactory)
    community = factory.SubFactory(CommunityFactory)
    institution = factory.SubFactory(InstitutionFactory)
    researcher = factory.SubFactory(ResearcherFactory)
    reference_id = factory.LazyAttribute(lambda n: faker.uuid4()[:50])
    viewed = factory.Faker('boolean')
    created = factory.Faker('date_time_this_year')
