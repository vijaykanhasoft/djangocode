from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hotel import models as hotel_models


def room_exists(room_id, hotel):
    try:
        room = hotel_models.ClientRoomInformation.objects.get(id=room_id, hotel=hotel)
        return room
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"room": {"message": "room does not exists"}})
