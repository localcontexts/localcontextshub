from api.base.views import *
from api.base import views as base_views
from rest_framework.views import APIView
from rest_framework.decorators import action
from . import serializers as v2_serializers
from rest_framework.viewsets import ViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from institutions.models import Institution
from accounts.models import Subscription
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

# class ApiKeyAuthentication(BaseAuthentication):
#     VALID_USER_IDS = [int(id_str) for id_str in settings.SF_VALID_USER_IDS.split()]

#     def authenticate(self, request):
#         api_key = request.headers.get('X-Api-Key')

#         if not api_key:
#             return None

#         try:
#             user = User.objects.get(user_profile__api_key=api_key)
#         except User.DoesNotExist:
#             raise AuthenticationFailed('Invalid API key')

#         # Check if the authenticated user is in the list of valid user IDs
#         if user.id not in self.VALID_USER_IDS:
#             raise AuthenticationFailed('Unauthorized user')

#         return (user, None)

class APIOverview(APIView):
    def get(self, request, format=None):
        api_urls = {
            'server': reverse('api-overview', request=request, format=format),
            'projects_list': '/projects/',
            'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
            'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'projects_by_user_id': '/projects/users/<USER_ID>/',
            'projects_by_institution_id': '/projects/institutions/<INSTITUTION_ID>/',
            'projects_by_researcher_id': '/projects/researchers/<RESEARCHER_ID>/',
            'open_to_collaborate_notice': '/notices/open_to_collaborate/',
            'api_documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources',
        }
        return Response(api_urls)

class OpenToCollaborateNotice(APIView):
    def get(self, request):
        api_urls = {
            'notice_type': 'open_to_collaborate',
            'name': 'Open to Collaborate Notice',
            'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
            'img_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.png',
            'svg_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.svg',
            'usage_guide_ci_notices': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf',
        }
        return Response(api_urls)

class ProjectList(generics.ListAPIView):
    permission_classes = [HasAPIKey]
    queryset = Project.objects.exclude(project_privacy='Private')
    serializer_class = ProjectOverviewSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', '$title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

class ProjectDetail(generics.RetrieveAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    lookup_field = 'unique_id'
    queryset = Project.objects.exclude(project_privacy='Private')

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return ProjectSerializer
        else:
            return ProjectNoNoticeSerializer
    
    def get_object(self):
        try:
            unique_id = self.kwargs.get('unique_id')
            obj = self.queryset.get(unique_id=unique_id)
            return obj
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

class ProjectsByIdViewSet(ViewSet):
    permission_classes = [HasAPIKey | IsAuthenticated]
    def projects_by_user(self, request, pk):
        try:
            useracct = User.objects.get(id=pk)
            projects = Project.objects.filter(project_creator=useracct).exclude(project_privacy='Private')
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
    permission_classes = [HasAPIKey | IsAuthenticated]

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

class GetUserAPIView(APIView):
    # authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

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
    # authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

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
            field_name = account_type_to_field.get(account_type)
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

            subscription, created = Subscription.objects.get_or_create(**filter_kwargs)
            if created:
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