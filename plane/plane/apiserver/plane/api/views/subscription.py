import json
from django.http import JsonResponse
import stripe
from django.conf import settings
from rest_framework import viewsets
from plane.api.views.base import BaseAPIView
from . import BaseViewSet
from plane.api.serializers.subscription import (
    SubscriptionSerializer
)
from plane.db.models import Workspace
from plane.db.models.subscription import Subscription

from plane.api.permissions import WorkSpaceBasePermission, WorkSpaceAdminPermission
from django.shortcuts import redirect

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionViewset(BaseViewSet):
    model = Subscription
    serializer_class = SubscriptionSerializer
    permission_classes = [
        WorkSpaceAdminPermission
    ]

    filterset_fields = [
        "workspace_id",
    ]

class CreateSubscription(BaseAPIView):
    def post(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        customer_id = workspace.stripe_customer_id
        data = request.data 
        try:
            checkout_session = stripe.checkout.Session.create(
                customer = customer_id,
                line_items = [
                    {
                        'price' : data['price_id'],
                        'quantity' : 1
                    }
                ],
                mode = 'suscription',
                success_url = "http://127.0.0.1:3000/"+"?session_id={CHECKOUT_SESSION_ID}",
                cancel_url = "http://127.0.0.1:3000/",
            )
            return redirect(checkout_session.url, code=303)
        except Exception as err:
            raise err

class WebHook(BaseAPIView):
    def post(self , request):
        """
            This API handling the webhook .

            :return: returns event details as json response .
        """
        request_data = json.loads(request.body)
        if webhook_secret:
            # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            signature = request.META['HTTP_STRIPE_SIGNATURE']
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, 
                    sig_header=signature, 
                    secret=webhook_secret
                    )
                data = event['data']
            except ValueError as err:
                raise err
            except stripe.error.SignatureVerificationError as err:
                raise err
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']

        if event_type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
            print("-----checkout.session.completed----->",data['object']['customer'])
        elif event_type == 'invoice.paid':
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
            print("-----invoice.paid----->", data)
        elif event_type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
            print("-----invoice.payment_failed----->",data)
        else:
            print('Unhandled event type {}'.format(event_type))
        
        return JsonResponse(success=True, safe=False)