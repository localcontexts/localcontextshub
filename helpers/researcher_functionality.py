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


class AllowedUserActions(Enum):
    EDIT = 1
    DOWNLOAD = 2


def allowed_researcher_project_actions(project: Project, project_creator: User, researcher: User):
    # Todo: get enum state based on input
    project_visibility = ''
    project_creator_subscription_state = ''
    researcher_relationship_to_project = ''
