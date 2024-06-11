from enum import Enum

from django.contrib.auth.models import User

from helpers.utils import project_creator_is_subscribed
from projects.models import Project, ProjectContributors


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


def get_project_visibility_enum(project: Project) -> ProjectVisibility:
    if project.PRIVACY_LEVEL == Project.PRIVACY_LEVEL['Public']:
        return ProjectVisibility.PUBLIC
    elif project.PRIVACY_LEVEL == Project.PRIVACY_LEVEL['Contributor']:
        return ProjectVisibility.CONTRIBUTOR_SHARED
    return ProjectVisibility.PRIVATE


def get_project_creator_subscription_state_enum(project: Project) -> UserSubscriptionState:
    if project_creator_is_subscribed(project):
        return UserSubscriptionState.SUBSCRIBED
    return UserSubscriptionState.UNSUBSCRIBED


def get_researcher_relationship_to_project_enum(researcher: User, project: Project) -> ResearcherRelationshipToProject:
    if project.project_creator == researcher:
        return ResearcherRelationshipToProject.CREATOR

    project_contributors = ProjectContributors.objects.filter(project=project)
    if project_contributors.is_user_contributor(researcher):
        return ResearcherRelationshipToProject.CONTRIBUTOR

    return ResearcherRelationshipToProject.NOT_ASSOCIATED


def allowed_researcher_project_actions(researcher: User, project: Project,):
    project_visibility = get_project_visibility_enum(project)
    project_creator_subscription_state = get_project_creator_subscription_state_enum(project)
    researcher_relationship_to_project = get_researcher_relationship_to_project_enum(researcher, project)
