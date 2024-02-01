from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .serializers import *
from projects.models import Project
from helpers.models import Notice
from projects.models import ProjectCreator
from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import User

@api_view(['GET'])
def apiOverview(request, format=None):
    email = request.query_params.get('email', None)
    api_urls = {
        'get_user': {
            'url': '/users?email=<email>',
            'description': 'Get user details by providing the email parameter.',
            'parameters': {
                'email': 'The email of the user to retrieve.',
            },
            'headers': {
                'X-Api-Key': 'Your-API-Key-Here',
            },
        },
        'projects_list': reverse('api-projects', request=request, format=format),
        'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
        'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
        'projects_by_user_id': '/projects/users/<USER_ID>/',
        'projects_by_institution_id': '/projects/institutions/<INSTITUTION_ID>/',
        'institution_projects_by_providers_id': '/projects/institutions/<INSTITUTION_ID>/<PROVIDERS_ID>',
        'projects_by_researcher_id': '/projects/researchers/<RESEARCHER_ID>/',
        'open_to_collaborate_notice': reverse('api-open-to-collaborate', request=request, format=format),
        'api_documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
        'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
    }
    return Response(api_urls)

@api_view(['GET'])
def openToCollaborateNotice(request):
    api_urls = {
        'notice_type': 'open_to_collaborate',
        'name': 'Open to Collaborate Notice',
        'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
        'img_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.png',
        'svg_url': f'https://storage.googleapis.com/{settings.STORAGE_BUCKET}/labels/notices/ci-open-to-collaborate.svg',
        'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
    }
    return Response(api_urls)

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.exclude(project_privacy='Private')
    serializer_class = ProjectOverviewSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', 'title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

#TODO: Add option to pass Providers ID using Project Detail search
class ProjectDetail(generics.RetrieveAPIView):
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


@api_view(['GET'])
def project_detail_providers(request, providers_id):
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

@api_view(['GET'])
def projects_by_user(request, pk):
    try:
        user = User.objects.get(id=pk)
        projects = Project.objects.filter(project_creator=user).exclude(project_privacy='Private')
        serializer = ProjectOverviewSerializer(projects, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_institution(request, institution_id, providers_id=None):
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

@api_view(['GET'])
@permission_classes([HasAPIKey | IsAuthenticated])
def get_user(request):
    email = request.query_params.get('email', None)
    if not email:
        return Response({"error": "Email parameter is required in the query parameters."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        serializer = GetUserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_researcher(request, researcher_id):
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

class MultiProjectListDetail(ViewSet):

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
