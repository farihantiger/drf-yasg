from django.conf.urls import url
from drf_openapi.entities import VersionedSerializers
from rest_framework import permissions, serializers, versioning
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from drf_yasg.drf_openapi_shim import view_config
from testproj.urls import SchemaView


class SnippetSerializerV1(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    v1field = serializers.IntegerField(required=True, help_text="field on V1 serializer")

    class Meta:
        error_status_codes = {
            HTTP_400_BAD_REQUEST: 'Bad Request'
        }


class SnippetSerializerV2(SnippetSerializerV1):
    title = serializers.CharField(required=True, max_length=100)
    v2field = serializers.IntegerField(required=True, help_text="field on V2 serializer")


class SnippetSerializer(VersionedSerializers):
    """
    Changelog:

    * **v1.0**: `title` is optional
    * **v2.0**: `title` is required
    """

    VERSION_MAP = (
        ('>=1.0, <2.0', SnippetSerializerV1),
        ('>=2.0', SnippetSerializerV2),
    )


class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    versioning_class = versioning.URLPathVersioning
    permission_classes = (permissions.AllowAny,)

    @view_config(response_serializer=SnippetSerializer, validate_response=True)
    def get(self, request, version, format=None):
        snippets = [{'title': 'snippet', 'v1field': 1, 'v2field': "bad value that should fail validation"}]
        return Response(snippets)

    @view_config(request_serializer=SnippetSerializer, response_serializer=SnippetSerializer)
    def post(self, request, version, format=None):
        pass


class VersionedSchemaView(SchemaView):
    versioning_class = versioning.URLPathVersioning


VERSION_PREFIX_URL = r"^v(?P<version>1.0|2.0)/"

urlpatterns = [
    url(VERSION_PREFIX_URL + r"snippets/$", SnippetList.as_view()),
    url(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(), name='vschema-json'),
]