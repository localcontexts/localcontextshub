from itertools import chain
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from . import serializers as v2_serializers
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter

from api.base.views import *
from api.base import views as base_views
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher
from accounts.models import Subscription
from datetime import datetime
from api.models import AccountAPIKey

'''
VARIABLE NOTES
- self.request.user or request.user = The API key being used is considered the user in this instance.
The model being referenced is AccountAPIKey.

ERROR MESSAGES TO USE:
1. For calls made without API Keys: "Authentation not provided"
2. For invalid API Keys (deleted, revoked, expired): "Invalid API key"
3. For actions trying to be made by unsubscribed, uncertified, or unapproved accounts:
    "Your account must be Subscribed, Certified, or Confirmed to perform this action."
4. For actions trying to be made by an account that is not the owner/creator of the project:
    "You do not have permission to view this project."
5. For actions trying to be made by an account that does not have access to the call:
    "You do not have permission to view this call."
6. For invalid project IDs passed: "Project does not exist."
7. For calls that require UUID but wrong ID is passed:
    "Invalid Project ID Provided."
'''

'''
APIKeyAuthentication checks a valid API Key was passed. API Key from user will be the encrypted key. 
If no API key provided, or an invalid key (expired/revoked) is provided, raise AuthenticationFailed.
'''
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-Api-Key')

        if not api_key:
            raise AuthenticationFailed('Authentication not provided')

        try:
            account = AccountAPIKey.objects.get(encrypted_key=api_key) 
        except AccountAPIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

        return (account, None)
    
'''
Checks for active status on subscriptions, service providers and members accounts.
If inactive, message appears.
TODO: Add is_certified and is_developer check for service providers and developers.
'''
class IsActive(BasePermission):
    message = "Your account must be Subscribed, Certified, or Confirmed to perform this action."

    def has_permission(self, request, view):
        account = request.user

        if account.researcher and account.researcher.is_subscribed:
            return True
        elif account.institution and account.institution.is_subscribed:
            return True
        elif account.community and account.community.is_approved:
            return True
        
        return False

'''
Checks that key is for a developer (user) account that has superuser access.
If not, permission blocked.
'''
class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.developer.is_superuser:
                return True
        except:
            return False
        
class IsActiveCreatorFilter(filters.BaseFilterBackend):
    """
    Filter that only allows users to see public projects and their own created projects if they are Active.
    Otherwise, they can only see projects that are not private.
    """
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
   institution_id = NumberFilter(field_name='project_creator_project__institution', lookup_expr='exact')
   researcher_id = NumberFilter(field_name='project_creator_project__researcher', lookup_expr='exact')
   community_id = NumberFilter(field_name='project_creator_project__community', lookup_expr='exact')
   user_id = NumberFilter(field_name='project_creator', lookup_expr='exact')
   title = CharFilter(field_name='title', lookup_expr='iregex')

   class Meta:
       model = Project
       fields = ['institution_id', 'researcher_id', 'community_id', 'user_id', 'title', 'providers_id', 'unique_id'] 

class APIOverview(APIView):
    def get(self, request, format=None):
        api_urls = {
            'server': reverse('api-overview', request=request, format=format),
            'projects_list': '/projects/',
            'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
            'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'multi_project_date_modified':'/projects/date_modified/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'open_to_collaborate_notice': '/notices/open_to_collaborate/',
            'api_documentation': 'https://github.com/localcontexts/localcontextshub/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
        }
        return Response(api_urls)

class OpenToCollaborateNotice(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsActive]

    def get(self, request):
        account = request.user
        if not account.community:
            if account.institution:
                profile_url = reverse('public-institution', request=request, kwargs={'pk': account.institution.id})
            elif account.researcher:
                profile_url = reverse('public-researcher', request=request, kwargs={'pk': account.researcher.id})

            api_urls = {
                'notice_type': 'open_to_collaborate',
                'name': 'Open to Collaborate Notice',
                'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
                'profile_url': profile_url,
                'img_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.png',
                'svg_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.svg',
                'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
            }
            return Response(api_urls)
        else:
            raise PermissionDenied("You do not have permission to view this call.")

class ProjectList(generics.ListAPIView):
    authentication_classes = [APIKeyAuthentication]

    serializer_class = v2_serializers.ProjectOverviewSerializer
    filter_backends = [IsActiveCreatorFilter, DjangoFilterBackend,]
    filterset_class = ProjectListFilterSet

    def get_queryset(self):
        queryset = self.filter_queryset(Project.objects.filter(project_privacy='Public'))
        return queryset

class ProjectDetail(generics.RetrieveAPIView):
    authentication_classes = [APIKeyAuthentication]
    filter_backends = [IsActiveCreatorFilter]
    lookup_field = 'unique_id'

    def get_queryset(self):
        queryset = self.filter_queryset(Project.objects.filter(project_privacy='Public'))
        return queryset

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return v2_serializers.ProjectSerializer
        else:
            return v2_serializers.ProjectNoNoticeSerializer
    
    def get_object(self):
        try:
            queryset = self.get_queryset()
            unique_id = self.kwargs.get('unique_id')
            if queryset.filter(unique_id=unique_id).exists():
                return queryset.get(unique_id=unique_id)
            elif Project.objects.get(unique_id=unique_id):
                raise PermissionDenied("You do not have permission to view this call.")

        except Project.DoesNotExist:
            raise Http404("Project does not exist.")
            # TODO: check to see why this message won't show properly

        
class MultiProjectListDetail(ViewSet):
    authentication_classes = [APIKeyAuthentication]
    filter_backends = [IsActiveCreatorFilter]

    def get_queryset(self):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, Project.objects.filter(project_privacy='Public'), self)
        return queryset

    def multisearch(self, request, unique_id):
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
                        {"detail": "You do not have permission to view this project."}, 
                        status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(
                        {"detail": "Project does not exist."}, 
                        status=status.HTTP_404_NOT_FOUND)

            notices = project.filter(Q(project_notice__isnull=False) & (Q(bc_labels__isnull=True) & Q(tk_labels__isnull=True))) 
            labels = project.filter(Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)).distinct()
            no_notice_labels = project.filter(Q(project_notice__isnull=True) & (Q(bc_labels__isnull=True) & Q(tk_labels__isnull=True))).distinct()

            notices_serializer = ProjectSerializer(notices, many=True)
            labels_serializer = ProjectNoNoticeSerializer(labels, many=True)
            no_notice_labels_serializer = ProjectNoNoticeSerializer(no_notice_labels, many=True)

            return Response({
                "notices_only":notices_serializer.data,
                "labels_only":labels_serializer.data,
                "no_labels_or_notices":no_notice_labels_serializer.data
            })
        except:
            return Response(
                {"detail": "Invalid Project ID Provided."}, 
                status=status.HTTP_404_NOT_FOUND)
    
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
                        {"detail": "You do not have permission to view this project."}, 
                        status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(
                        {"detail": "Project does not exist."}, 
                        status=status.HTTP_404_NOT_FOUND)

            serializer = ProjectDateModified(project, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {"detail": "Invalid Project ID Provided."}, 
                status=status.HTTP_404_NOT_FOUND)

# SALESFORCE CALLS
class GetUserAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsSuperuser]

    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response({"error": "Email parameter is required in the query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            serializer = GetUserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class SubscriptionAPI(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsSuperuser]

    def get(self, request):
        date_last_updated = request.query_params.get('date_last_updated')
        if date_last_updated is not None:
            try:
                date_last_updated = datetime.strptime(date_last_updated, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM:SSZ'}, status=status.HTTP_400_BAD_REQUEST)

            subscriptions = Subscription.objects.filter(date_last_updated__gt=date_last_updated)
            serializer = GetSubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'date_last_updated parameter is required'}, status=status.HTTP_400_BAD_REQUEST)


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
                    return Response({'success': 'The record is created.'}, status=HTTP_201_CREATED)
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