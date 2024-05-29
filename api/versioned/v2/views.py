from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from . import serializers as v2_serializers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.permissions import HasAPIKey, BaseHasAPIKey

from api.base.views import *
from api.base import views as base_views
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher
from accounts.models import Subscription
from datetime import datetime
from api.models import AccountAPIKey
from helpers.utils import decrypt_api_key

'''
VARIABLE NOTES
- self.request.user or request.user = The API key being used is considered the user in this instance.
The model being referenced is AccountAPIKey.
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

class APIOverview(APIView):
    def get(self, request, format=None):
        api_urls = {
            'server': reverse('api-overview', request=request, format=format),
            'projects_list': '/projects/',
            'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
            'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'projects_by_user_id': '/projects/users/<USER_ID>/',
            'projects_by_institution_id': '/projects/institutions/<INSTITUTION_ID>/',
            'institution_projects_by_providers_id': '/projects/institutions/<INSTITUTION_ID>/<PROVIDERS_ID>',
            'projects_by_researcher_id': '/projects/researchers/<RESEARCHER_ID>/',
            'open_to_collaborate_notice': '/notices/open_to_collaborate/',
            'api_documentation': 'https://github.com/localcontexts/localcontextshub/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
        }
        return Response(api_urls)

class OpenToCollaborateNotice(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsActive]

    def get(self, request):
        if not request.user.community:
            api_urls = {
                'notice_type': 'open_to_collaborate',
                'name': 'Open to Collaborate Notice',
                'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
                'img_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.png',
                'svg_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.svg',
                'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
            }
            return Response(api_urls)
        else:
            raise AuthenticationFailed('Unauthorized user')

class ProjectList(generics.ListAPIView):
    authentication_classes = [APIKeyAuthentication]

    serializer_class = ProjectOverviewSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', '$title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

    def get_queryset(self):
        queryset = []
        
        if self.request.user.institution:
            account = self.request.user.institution
            if account.is_subscribed:
                creators = ProjectCreator.objects.filter(institution=account)
            else: 
                creators = ProjectCreator.objects.filter(institution=account).exclude(project__project_privacy='Private')
            for x in creators:
                queryset.append(x.project)

        elif self.request.user.researcher:
            account = self.request.user.researcher
            if account.is_subscribed:
                creators = ProjectCreator.objects.filter(researcher=account)
            else: 
                creators = ProjectCreator.objects.filter(researcher=account).exclude(project__project_privacy='Private')
            for x in creators:
                queryset.append(x.project)
        
        elif self.request.user.community:
            account = self.request.user.community
            if account.is_approved:
                creators = ProjectCreator.objects.filter(community=account)
            else: 
                creators = ProjectCreator.objects.filter(community=account).exclude(project__project_privacy='Private')
            for x in creators:
                queryset.append(x.project)

        return queryset

class ProjectDetail(generics.RetrieveAPIView):
    authentication_classes = [APIKeyAuthentication]
    lookup_field = 'unique_id'

    def get_queryset(self):
        if self.request.user.institution:
            account = self.request.user.institution
            queryset = Project.objects.filter(project_creator__institution_created_project=account)
        elif self.request.user.researcher:
            account = self.request.user.researcher
            queryset = Project.objects.filter(project_creator=account)
        elif self.request.user.community:
            account = self.request.user.community
            queryset = Project.objects.filter(project_creator=account)
        elif self.request.user.developer:
            account = self.request.user.developer
            queryset = Project.objects.filter(project_creator=account)

        print(account, queryset)
        return queryset

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return ProjectSerializer
        else:
            return ProjectNoNoticeSerializer
    
    # def get_object(self):
    #     try:
    #         unique_id = self.kwargs.get('unique_id')
    #         obj = self.queryset.get(unique_id=unique_id)
    #         return obj
    #     except Project.DoesNotExist:
    #         raise Http404("Project does not exist")

class ProjectsByIdViewSet(ViewSet):
    authentication_classes = [APIKeyAuthentication]

    def projects_by_user(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            projects = Project.objects.filter(project_creator=user).exclude(project_privacy='Private')
            serializer = ProjectOverviewSerializer(projects, many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def projects_by_institution(self, request, institution_id, providers_id=None):
        try:
            institution = Institution.objects.get(id=institution_id)

            projects = []
            creators = ProjectCreator.objects.filter(institution=institution)
            if providers_id != None:
                for x in creators:
                    if x.project.providers_id == providers_id:
                        projects.append(x.project)
            else:
                for x in creators:
                    projects.append(x.project)
            
            serializer = ProjectOverviewSerializer(projects, many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def projects_by_researcher(self, request, researcher_id):
        try:
            researcher = Researcher.objects.get(id=researcher_id)

            projects = []
            creators = ProjectCreator.objects.filter(researcher=researcher)
            for x in creators:
                projects.append(x.project)

            serializers = ProjectOverviewSerializer(projects, many=True)
            return Response(serializers.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

#TODO: remove this function or convert it so that the project detail (list view) can be used using either projectID or providersID. Two URLs that use one call. projects/external url would be removed
# Make this a filter instead?
    def project_detail_providers(self, request, providers_id):
        try:
            project = Project.objects.get(providers_id=providers_id)
            if project.project_privacy == 'Public' or project.project_privacy == 'Contributor':
                if project.has_notice():
                    serializer = ProjectSerializer(project, many=False)
                else:
                    serializer = ProjectNoNoticeSerializer(project, many=False)
                
                return Response(serializer.data)
            else:
                raise PermissionDenied({"message":"You don't have permission to view this project", "providers_id": providers_id})
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class MultiProjectListDetail(ViewSet):
    authentication_classes = [APIKeyAuthentication]

    def multisearch(self, request, unique_id):
        try:
            project = Project.objects.all()

            if unique_id is not None:
                unique_id = unique_id.split(',')
                query= Q()
                for x in unique_id:
                    q = Q(unique_id=x)
                    query |= q  
                project=project.filter(query).exclude(project_privacy='Private')
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
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def multisearch_date(self, request, unique_id):
        try:
            project = Project.objects.all()

            if unique_id is not None:
                unique_id = unique_id.split(',')
                query= Q()
                for x in unique_id:
                    q = Q(unique_id=x)
                    query |= q  
                project=project.filter(query).exclude(project_privacy='Private')

            serializer = ProjectDateModified(project, many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

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