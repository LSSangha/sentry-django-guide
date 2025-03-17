import json

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import InventorySerializer
from .models import Inventory

import sentry_sdk
from sentry_sdk import capture_message, set_context, set_tag, set_user
from django.http import JsonResponse


InventoryData = [
    {"name": "wrench", "count": 1},
    {"name": "nails", "count": 1},
    {"name": "hammer", "count": 1},
]


def find_in_inventory(itemId):
    for item in InventoryData:
        if item["name"] == itemId:
            return item
    raise Exception("Item : " + itemId + " not in inventory ")


def process_order(cart):
    sentry_sdk.add_breadcrumb(
        category="Process Order",
        message="Step taken to process an order",
        level="info",
    )
    global InventoryData
    tempInventory = InventoryData
    for item in cart:
        itemID = item["id"]
        inventoryItem = find_in_inventory(itemID)
        if inventoryItem["count"] <= 0:
            raise Exception("Not enough inventory for " + itemID)
        else:
            inventoryItem["count"] -= 1
            print(
                "Success: "
                + itemID
                + " was purchased, remaining stock is "
                + str(inventoryItem["count"])
            )
    InventoryData = tempInventory


class SentryContextMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.body:
            body_unicode = request.body.decode("utf-8")
            order = json.loads(body_unicode)

            # Enhanced user context
            user_data = {
                "email": order.get("email"),
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }
            set_user(user_data)

        transactionId = request.headers.get("X-Transaction-ID")
        sessionId = request.headers.get("X-Session-ID")

        # Enhanced context and tags
        set_context("request_metadata", {
            "transaction_id": transactionId,
            "session_id": sessionId,
            "http_method": request.method,
            "path": request.path,
        })

        set_tag("transaction_type", "inventory")
        if sessionId:
            set_tag("session_id", sessionId)

        # Add inventory state to context
        set_context("inventory_state", {
            "current_inventory": InventoryData,
            "total_items": sum(item["count"] for item in InventoryData)
        })

        return super(SentryContextMixin, self).dispatch(request, *args, **kwargs)


class InventoreyView(SentryContextMixin, APIView):

    def get(self, request):
        try:
            results = InventorySerializer(InventoryData, many=True).data
            return Response(results)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response({"error": "Failed to fetch inventory"}, status=500)

    def post(self, request, format=None):
        try:
            body_unicode = request.body.decode("utf-8")
            order = json.loads(body_unicode)
            cart = order["cart"]
            
            # Add order context
            set_context("order_details", {
                "cart_items": len(cart),
                "order_total": sum(item.get("quantity", 1) for item in cart)
            })
            
            process_order(cart)
            return Response(InventoryData)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            
            # Return error with user feedback form
            event_id = sentry_sdk.last_event_id()
            return JsonResponse({
                "error": str(e),
                "sentry": {
                    "event_id": event_id,
                    "dsn": "https://d655584d05f14c58b86e9034aab6817f@o447951.ingest.us.sentry.io/5461230"
                }
            }, status=500)


class HandledErrorView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the handled function",
            level="info",
        )
        try:
            "2" + 2
        except Exception as err:
            sentry_sdk.capture_exception(err)
        return Response()


class UnHandledErrorView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the unhandled function",
            level="info",
        )
        obj = {}
        obj["keyDoesntExist"]
        return Response()


class CaptureMessageView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the Capture Message function",
            level="info",
        )
        sentry_sdk.capture_message("You caught me!", "fatal")

        return Response()
