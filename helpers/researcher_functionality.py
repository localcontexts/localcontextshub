from enum import Enum

from django.contrib.auth.models import User

from projects.models import Project, ProjectContributors
from researchers.models import Researcher
from institutions.models import Institution


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


def project_creator_is_subscribed(project: Project) -> bool:
    project_creator_user = project.project_creator

    if Researcher.objects.filter(is_subscribed=True, user=project_creator_user).exists():
        return True

    if Institution.objects.filter(is_subscribed=True, community_creator=project_creator_user).exists():
        return True

    return False


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
    # Todo: transform input args into enums
    project_visibility = get_project_visibility_enum(project)
    project_creator_subscription_state = get_project_creator_subscription_state_enum(project)
    researcher_relationship_to_project = get_researcher_relationship_to_project_enum(researcher, project)
