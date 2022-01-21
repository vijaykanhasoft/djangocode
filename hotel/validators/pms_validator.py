from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hotel import models as hotel_models


def pms_exists(id, hotel):
    try:
        pms = hotel_models.PMS.objects.get(id=id, hotel=hotel)
        return pms
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"pms": {"message": "pms does not exists"}})


def hotel_pms(hotel):
    if hotel.is_pms_linked:
        return hotel.pms
    else:
        raise serializers.ValidationError({"pms": {"message": "pms configuration not found"}})

def connected_pms_room(pms_room):
    try:
        room = hotel_models.ClientRoomInformation.objects.get(pms_room=pms_room, hotel=pms_room.pms.hotel)
        return room
    except ObjectDoesNotExist:
        return None

def connected_pms_rate(pms_rate):
    try:
        room = hotel_models.ClientRoomInformation.objects.get(pms_rate=pms_rate, hotel=pms_rate.pms.hotel)
        return room
    except ObjectDoesNotExist:
        return None




