# Third party imports
from rest_framework.response import Response
from rest_framework import status

from sentry_sdk import capture_exception

# Module imports
from plane.api.serializers import (
    UserSerializer,
)

from plane.api.views.base import BaseViewSet, BaseAPIView
from plane.db.models import User, Workspace

class UserEndpoint(BaseViewSet):
    serializer_class = UserSerializer
    model = User

    def get_object(self):
        return self.request.user

    def retrieve(self, request):
        try:
            workspace = Workspace.objects.get(pk=request.user.last_workspace_id)
            return Response(
                {"user": UserSerializer(request.user).data, "slug": workspace.slug}
            )
        except Workspace.DoesNotExist:
            return Response({"user": UserSerializer(request.user).data, "slug": None})
        except Exception as e:
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateUserOnBoardedEndpoint(BaseAPIView):
    def patch(self, request):
        try:
            user = User.objects.get(pk=request.user.id)
            user.is_onboarded = request.data.get("is_onboarded", False)
            user.save()
            return Response(
                {"message": "Updated successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )
