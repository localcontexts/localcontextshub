from enum import Enum

from django.contrib.auth.models import User

from projects.models import Project


class ProjectVisibility(Enum):
    PUBLIC = 1
    CONTRIBUTOR_SHARED = 2          # This is a private project that has contributors
    PRIVATE = 3


class UserSubscriptionState(Enum):
    SUBSCRIBED = 1
    UNSUBSCRIBED = 2


class ResearcherRelationshipToProject(Enum):
    CREATOR = 1
    CONTRIBUTOR = 2
    NOT_ASSOCIATED = 3      # This is when user is: not a creator, and not a contributor


def allowed_researcher_project_actions(researcher: User, project_creator: User, project: Project):
    # Todo: get enum state based on input
    researcher_relationship_to_project = ''
    project_creator_subscription_state = ''
    project_visibility = ''
