from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from .serializers import *
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import Project

@api_view(['GET'])
def apiOverview(request, format=None):
    api_urls = {
        'projects list': reverse('api-projects', request=request, format=format),
        'project detail': '/projects/<PROJECT_UNIQUE_ID>/',
        'projects by username': '/projects/users/<USERNAME>/',
        'projects by institution id': '/projects/institutions/<INSTITUTION_ID>/',
        'projects by researcher id': '/projects/researchers/<RESEARCHER_ID>/',
        'API Documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
        'Usage Guide for TK/BC Notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf',
        'Usage Guide for Institution Notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf',
        'Usage Guide for BC and TK Labels': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf',
    }
    return Response(api_urls)

@api_view(['GET'])
def projects(request):
    projects = Project.objects.exclude(project_privacy='Private')
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def project_detail(request, unique_id):
    try:
        project = Project.objects.get(unique_id=unique_id)
        if project.project_privacy == 'Public' or project.project_privacy == 'Discoverable':
            if project.has_notice():
                serializer = ProjectSerializer(project, many=False)
            else:
                serializer = ProjectNoNoticeSerializer(project, many=False)
            
            return Response(serializer.data)
        else:
            raise PermissionDenied({"message":"You don't have permission to view this project",
                                    "unique_id": unique_id})
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_user(request, username):
    user = User.objects.get(username__iexact=username)
    projects = Project.objects.filter(project_creator=user, project_privacy='Public')
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)
    projects = institution.projects.filter(project_privacy='Public')
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_researcher(request, researcher_id):
    researcher = Researcher.objects.get(id=researcher_id)
    projects = researcher.projects.filter(project_privacy='Public')
    serializers = ProjectOverviewSerializer(projects, many=True)
    return Response(serializers.data)

