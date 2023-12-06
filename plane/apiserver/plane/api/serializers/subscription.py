# Third party imports
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from .user import UserLiteSerializer
from .workspace import WorkSpaceSerializer

from plane.db.models import User, Workspace
from plane.db.models.pricing_plan import PricingPlan
from plane.db.models.subscription import Subscription

class SubscriptionSerializer(BaseSerializer):
    workspace_id = WorkSpaceSerializer(read_only=True)

    class Meta:
            model = Subscription
            fields = "__all__"
            read_only_fields = [
                "id",
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            ]
        