import json
from itertools import chain
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404

from rest_framework import generics, filters, status, serializers
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, NumberFilter, CharFilter, UUIDFilter
)
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import (
    extend_schema, inline_serializer, OpenApiResponse, OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from api.base import serializers as base_serializers
from api.views import HELPTEXT_CHOICES
from . import serializers as v2_serializers
from django.db.models import Q
from projects.models import Project
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher
from accounts.models import Subscription
from api.models import AccountAPIKey


'''
    USER API ERROR MESSAGES:
        1. For calls made without API Keys: `no_key`
        2. For invalid API Keys (deleted, revoked, expired): `invalid_key`
        3. For actions trying to be made by unsubscribed, uncertified, or unapproved accounts:
            `incomplete_account`
        4. For actions trying to be made by an account that is not the owner/creator of the
            project: `denied_project`
        5. For actions trying to be made by an account that does not have access to the call:
            `denied_call`
        6. For invalid project IDs passed: `no_project`
        7. For calls that require UUID but wrong ID is passed: `invalid_id`
'''
ERROR_MESSAGE_CHOICES = {
    'no_key': "Authentication not provided.",
    'invalid_key': "Invalid API key.",
    'incomplete_account': "Your account must be Subscribed, Certified, or Confirmed to perform this action.",
    'denied_project': "You do not have permission to view this project.",
    'denied_call': "You do not have permission to view this call.",
    'no_project': "Project does not exist.",
    'invalid_id': "Invalid Project ID Provided.",
    'email_required': "Email parameter is required in the query parameters."
}


class APIKeyAuthentication(BaseAuthentication):
    '''
        APIKeyAuthentication checks a valid API Key was passed. API Key from user will be the
        encrypted key. If no API key provided, or an invalid key (expired/revoked) is provided,
        raise AuthenticationFailed.

        self.request.user or request.user = The API key being used is considered the user in this
            instance. The model being referenced is AccountAPIKey.
    '''
    def authenticate(self, request):
        api_key = request.headers.get('X-Api-Key')

        if not api_key:
            raise AuthenticationFailed(ERROR_MESSAGE_CHOICES['no_key'])

        try:
            account = AccountAPIKey.objects.get(encrypted_key=api_key)
        except AccountAPIKey.DoesNotExist:
            raise AuthenticationFailed(ERROR_MESSAGE_CHOICES['invalid_key'])

        return (account, None)


# OpenAPI Schema for LC API Key Authentication
class MyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'api.versioned.v2.views.APIKeyAuthentication'  # full import path OR class ref
    name = 'LCHubAPIKey'  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-Api-Key',
        }


class IsActive(BasePermission):
    '''
        Checks for active status on subscriptions, service providers and members accounts.
        If inactive, message appears.
        TODO: Add is_certified and is_developer check for service providers and developers.
    '''
    message = ERROR_MESSAGE_CHOICES['incomplete_account']

    def has_permission(self, request, view):
        account = request.user

        if account.researcher and account.researcher.is_subscribed:
            return True
        elif account.institution and account.institution.is_subscribed:
            return True
        elif account.community and account.community.is_approved:
            return True

        return False


class IsSuperuser(BasePermission):
    '''
        Checks that key is for a developer (user) account that has superuser access.
        If not, permission blocked.
    '''
    def has_permission(self, request, view):
        try:
            if request.user.developer.is_superuser:
                return True
        except:
            return False


# FILTERS
class IsActiveCreatorFilter(filters.BaseFilterBackend):
    '''
        Filter that only allows users to see public projects and their own created projects
        if they are Active. Otherwise, they can only see projects that are not private.
    '''
    def filter_queryset(self, request, queryset, view):
        try:
            account = request.user
            if account.institution and account.institution.is_subscribed:
                projects_list = list(
                    chain(
                        account.institution.institution_created_project.all().values_list(
                            "project__unique_id", flat=True
                        ),  # institution created project ids
                        account.institution.contributing_institutions.all().values_list(
                            "project__unique_id", flat=True
                        ),  # projects where institution is contributor
                    )
                )

            elif account.researcher and account.researcher.is_subscribed:
                projects_list = list(
                    chain(
                        account.researcher.researcher_created_project.all().values_list(
                            "project__unique_id", flat=True
                        ),  # researcher created project ids
                        account.researcher.contributing_reserchers.all().values_list(
                            "project__unique_id", flat=True
                        ),  # projects where researcher is contributor
                    )
                )

            elif account.community and account.community.is_approved:
                projects_list = list(
                    chain(
                        account.community.community_created_project.all().values_list(
                            "project__unique_id", flat=True
                        ),  # community created project ids
                        account.community.contributing_communities.all().values_list(
                            "project__unique_id", flat=True
                        ),  # projects where community is contributor
                    )
                )

            projects = list(chain(
                queryset.values_list("unique_id", flat=True),
                projects_list
            ))
            project_ids = list(set(projects))
            return Project.objects.filter(unique_id__in=project_ids)

        except:
            return queryset

class ProjectListFilterSet(FilterSet):
    institution_id = NumberFilter(
       field_name='project_creator_project__institution', lookup_expr='exact',
       help_text=HELPTEXT_CHOICES['id']
    )
    researcher_id = NumberFilter(
       field_name='project_creator_project__researcher', lookup_expr='exact',
       help_text=HELPTEXT_CHOICES['id']
    )
    community_id = NumberFilter(
       field_name='project_creator_project__community', lookup_expr='exact',
       help_text=HELPTEXT_CHOICES['id']
    )
    user_id = NumberFilter(
        field_name='project_creator', lookup_expr='exact', help_text=HELPTEXT_CHOICES['id']
    )
    title = CharFilter(
        field_name='title', lookup_expr='iregex', help_text=HELPTEXT_CHOICES['title']
    )
    providers_id = CharFilter(help_text=HELPTEXT_CHOICES['providers_id'])
    unique_id = UUIDFilter(
        field_name='unique_id', lookup_expr='exact', help_text=HELPTEXT_CHOICES['unique_id']
    )

    class Meta:
        model = Project
        fields = [
            'institution_id', 'researcher_id', 'community_id', 'user_id', 'title',
            'providers_id', 'unique_id'
        ]


# PUBLIC API CALLS
class APIOverview(APIView):
    @extend_schema(
        request=None,
        description="Get a list of all possible endpoints.",
        operation_id= "api_overview",
        responses={
            200: inline_serializer(
                name = "APIOverview",
                fields = {
                    'projects_list': serializers.CharField(
                        help_text="Displays the path of the Projects List endpoint."
                    ),
                    'project_detail': serializers.CharField(
                        help_text="Displays the path of the Projects Detail endpoint."
                    ),
                    'multi_project_detail': serializers.CharField(
                        help_text="Displays the path of the Projects Detail endpoint when "
                            "searching for multiple Projects."
                    ),
                    'multi_project_date_modified': serializers.CharField(
                        help_text="Displays the path of the Project Date Modified endpoint when "
                            "searching for multiple Projects' modified date."
                    ),
                    'open_to_collaborate_notice': serializers.CharField(
                        help_text="Displays the path of the Open to Collaborate Notice endpoint."
                    ),
                    'api_documentation': serializers.URLField(
                        help_text="Displays the URL for the API Documentation."
                    ),
                    'usage_guides': serializers.URLField(
                        help_text="Displays the URL to all Notices and Labels Usage Guides"
                    )
                }
            )
        }
    )

    def get(self, request, format=None):
        api_urls = {
            'projects_list': '/projects/',
            'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
            'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'multi_project_date_modified':'/projects/multi/date_modified/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'open_to_collaborate_notice': '/notices/open_to_collaborate/',
            'api_documentation': 'https://github.com/localcontexts/localcontextshub/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources'
        }
        return Response(api_urls)


class OpenToCollaborateNotice(APIView):
    authentication_classes = [APIKeyAuthentication,]
    permission_classes = [IsActive,]

    @extend_schema(
        request=v2_serializers.OpenToCollaborationSerializer,
        description="Get information about the Open to Collaborate Notice.",
        operation_id="open_to_collaborate",
        responses={
            200: v2_serializers.OpenToCollaborationSerializer,
            401: OpenApiResponse(description='Error: Permission Denied'),
            403: OpenApiResponse(description='Error: Forbidden'),
        }
    )

    def get(self, request):
        if not request.user.community:
            notice_json_data = open('./localcontexts/static/json/Notices.json')
            notice_data = json.load(notice_json_data) #deserialize

            baseURL = f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/'
            for item in notice_data:
                notice_type = item['noticeType']
                if notice_type == 'open_to_collaborate':
                    name = item['noticeName']
                    img_url = baseURL + item['imgFileName']
                    svg_url = baseURL + item['svgFileName']
                    default_text = item['noticeDefaultText']

            with open(
                './localcontexts/static/json/NoticeTranslations.json', encoding="utf8"
            ) as translations_json_data:
                translations_data = json.load(translations_json_data)

            translations = []
            for item in translations_data:
                notice_type = item['noticeType']
                if notice_type == 'open_to_collaborate':
                    translated_name = item['noticeName']
                    language_tag = item['languageTag']
                    language = item['language']
                    translated_text = item['noticeDefaultText']

                    notice_translation = {
                        'translated_name': translated_name,
                        'language_tag': language_tag,
                        'language': language,
                        'language': language,
                        'translated_text': translated_text
                    }
                    translations.append(notice_translation)

            notice = {
                'notice_type': notice_type,
                'name': name,
                'img_url': img_url,
                'svg_url': svg_url,
                'default_text': default_text,
                'notice_translations': translations,
                'created': '2021-10-05T00:00:00.000Z',
                'updated': '2021-10-05T00:00:00.000Z'
            }

            data = {
                'notice': notice
            }

            if request.user.researcher:
                data['researcher'] = request.user.researcher
                data['institution'] = None
            elif request.user.institution:
                data['institution'] = request.user.institution
                data['researcher'] = None

            serializer = v2_serializers.OpenToCollaborationSerializer(
                data, context={'request': request}
            )
            return Response(serializer.data)
        else:
            raise PermissionDenied(ERROR_MESSAGE_CHOICES['denied_call'])

@extend_schema(
    request=v2_serializers.ProjectOverviewSerializer,
    description="Get a list of all Projects available through the Hub.",
    responses={
        200: v2_serializers.ProjectOverviewSerializer,
        403: OpenApiResponse(description='Error: Forbidden'),
    },
)
class ProjectList(generics.ListAPIView):
    authentication_classes = [APIKeyAuthentication]

    serializer_class = v2_serializers.ProjectOverviewSerializer
    filter_backends = [IsActiveCreatorFilter, DjangoFilterBackend,]
    filterset_class = ProjectListFilterSet

    def get_queryset(self):
        queryset = self.filter_queryset(Project.objects.filter(project_privacy='Public'))
        return queryset


@extend_schema(
    request=v2_serializers.ProjectSerializer,
    description="Loads the Project information based on the Project's unique_id.",
    responses={
        200: v2_serializers.ProjectSerializer,
        403: OpenApiResponse(description='Error: Forbidden'),
        404: OpenApiResponse(description='Error: Not Found'),
    },
    parameters=[
        OpenApiParameter(
            name="unique_id", description=HELPTEXT_CHOICES['unique_id'], required=True, type=OpenApiTypes.UUID, location="path"
        )
    ],
)
class ProjectDetail(generics.RetrieveAPIView):
    authentication_classes = [APIKeyAuthentication]
    serializer_class = v2_serializers.ProjectSerializer
    filter_backends = [IsActiveCreatorFilter]
    lookup_field = 'unique_id'

    def get_queryset(self):
        queryset = self.filter_queryset(Project.objects.filter(project_privacy='Public'))
        return queryset

    def get_object(self):
        try:
            queryset = self.get_queryset()
            unique_id = self.kwargs.get('unique_id')
            if queryset.filter(unique_id=unique_id).exists():
                return queryset.get(unique_id=unique_id)
            elif Project.objects.get(unique_id=unique_id):
                raise PermissionDenied(ERROR_MESSAGE_CHOICES['denied_call'])

        except Project.DoesNotExist:
            raise Http404(ERROR_MESSAGE_CHOICES['no_project'])
            # TODO: check to see why this message won't show properly


class MultiProjectListDetail(ViewSet):
    authentication_classes = [APIKeyAuthentication]
    filter_backends = [IsActiveCreatorFilter]
    serializer_class = v2_serializers.ProjectSerializer

    def get_queryset(self):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(
                self.request, Project.objects.filter(project_privacy='Public'), self
            )
        return queryset

    @extend_schema(
        request=v2_serializers.ProjectSerializer,
        parameters=[
            OpenApiParameter(
                "unique_id", required=True, type=OpenApiTypes.UUID, many=True,
                location=OpenApiParameter.PATH, description=HELPTEXT_CHOICES['unique_id']
            )
        ],
        description="Loads the Project information for all Projects whose unique_id is " \
            "included at the end of the path. NOTE: All unique_ids must be added with a comma " \
            "separating each unique_id (no spaces).",
        responses={
            200: v2_serializers.ProjectSerializer,
            403: OpenApiResponse(description='Error: Forbidden'),
            404: OpenApiResponse(description='Error: Not Found'),
        },
    )
    def multisearch(self, request, unique_id):
        try:
            unique_id = unique_id.split(',')
            query= Q()
            for x in unique_id:
                q = Q(unique_id=x)
                query |= q
            project=self.get_queryset().filter(query)

            if not project:
                if Project.objects.filter(project).exists():
                    return Response(
                        {"detail": ERROR_MESSAGE_CHOICES['denied_project']},
                        status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(
                        {"detail": ERROR_MESSAGE_CHOICES['no_project']},
                        status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(project, many=True, context={"request": request})

            return Response(serializer.data)
        except:
            return Response(
                {"detail": ERROR_MESSAGE_CHOICES['invalid_id']},
                status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=v2_serializers.ProjectDateModified,
        parameters=[
            OpenApiParameter(
                "unique_id", required=True, type=OpenApiTypes.UUID, many=True,
                location=OpenApiParameter.PATH, description=HELPTEXT_CHOICES['unique_id']
            )
        ],
        description="Loads the Project's date modified information for all Projects whose " \
            "unique_id is included at the end of the path. NOTE: All unique_ids must be added " \
            "with a comma separating each unique_id (no spaces).",
        responses={
            200: v2_serializers.ProjectDateModified,
            403: OpenApiResponse(description='Error: Forbidden'),
            404: OpenApiResponse(description='Error: Not Found'),
        },
    )
    def multisearch_date(self, request, unique_id):
        try:
            unique_id = unique_id.split(',')
            query= Q()
            for x in unique_id:
                q = Q(unique_id=x)
                query |= q
            project=self.get_queryset().filter(query)

            if not project:
                if Project.objects.filter(query).exists():
                    return Response(
                        {"detail": ERROR_MESSAGE_CHOICES['denied_project']},
                        status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(
                        {"detail": ERROR_MESSAGE_CHOICES['no_project']},
                        status=status.HTTP_404_NOT_FOUND)

            serializer = v2_serializers.ProjectDateModified(project, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {"detail": ERROR_MESSAGE_CHOICES['invalid_id']},
                status=status.HTTP_404_NOT_FOUND)

# SALESFORCE CALLS
@extend_schema(exclude=True)
class GetUserAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsSuperuser]

    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response(
                {"error": "Email parameter is required in the query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
            serializer = base_serializers.GetUserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(exclude=True)
class SubscriptionAPI(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsSuperuser]

    def get(self, request):
        date_last_updated = request.query_params.get('date_last_updated')
        if date_last_updated is not None:
            try:
                date_last_updated = datetime.strptime(date_last_updated, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM:SSZ'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscriptions = Subscription.objects.filter(date_last_updated__gt=date_last_updated)
            serializer = base_serializers.GetSubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'date_last_updated parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )


    def post(self, request):
        try:
            account_id = request.data.get('account_id')
            hub_id , account_type = account_id.split('_')
            user_count = request.data.get('users_count')
            api_key_count = request.data.get('api_key_count')
            project_count = request.data.get('project_count')
            notification_count = request.data.get('notification_count')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            date_last_updated = request.data.get('date_last_updated')

            account_type_to_field = {
                'i': 'institution_id',
                'c': 'community_id',
                'r': 'researcher_id'
            }
            field_to_model = {
                'institution_id': Institution,
                'community_id': Community,
                'researcher_id': Researcher
            }

            field_name = account_type_to_field.get(account_type)
            model_class = field_to_model.get(field_name)
            if not field_name:
                return Response(
                    {'error': 'Failed to create Subscription. Invalid account_type provided.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            filter_kwargs = {
                field_name: hub_id,
                'defaults': {
                    'users_count': user_count,
                    'api_key_count': api_key_count,
                    'project_count': project_count,
                    'notification_count': notification_count,
                    'start_date': start_date,
                    'end_date': end_date,
                    'date_last_updated': date_last_updated
                }
            }
            with transaction.atomic():
                subscription, created = Subscription.objects.get_or_create(**filter_kwargs)
                if created:
                    subscriber = get_object_or_404(model_class, id=hub_id)
                    subscriber.is_subscribed = True
                    subscriber.save()
                    return Response(
                        {'success': 'The record is created.'}, status=HTTP_201_CREATED
                    )
                else:
                    subscription.users_count = user_count
                    subscription.api_key_count = api_key_count
                    subscription.project_count = project_count
                    subscription.notification_count = notification_count
                    subscription.start_date = start_date
                    subscription.end_date = end_date
                    subscription.date_last_updated = date_last_updated
                    subscription.save()
                    return Response({'success': 'The record is updated.'},status=HTTP_200_OK)

        except IntegrityError as e:
            if 'violates foreign key constraint' in str(e):
                return Response(
                    {'error': 'Failed to create Subscription. This record violates foreign key constraint.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': 'An unexpected error occurred.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )