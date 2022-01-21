from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hotel import models as hotel_models


def unused_hotel(hotel_id):
    try:
        hotel = hotel_models.HotelOTA.objects.get(id=hotel_id, client=None)
        return hotel
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": "hotel already belongs to a client"}})


def owned_room_by_hotel(room_id, hotel_id):
    try:
        room = hotel_models.ClientRoomInformation.objects.get(id=room_id, hotel_id=hotel_id)
        return room
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"room": {"message": "room does not exists"}})


def client_hotel_subscription_exists(subscription_id, message="hotel does not exists"):
    try:
        hotel = hotel_models.HotelOTA.objects.get(subscription_id=subscription_id)
        return hotel
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": message}})

def hotel_exists(hotel_id, message="hotel does not exists"):
    try:
        hotel = hotel_models.HotelOTA.objects.get(id=hotel_id)
        return hotel
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": message}})


def client_hotel_exists(hotel_id, message="client hotel does not exists"):
    try:
        hotel = hotel_models.ClientHotel.objects.get(id=hotel_id)
        return hotel
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": message}})


def hotel_data_model_exists(hotel):
    try:
        hotel_data_model = hotel_models.HotelDataModel.objects.get(hotel=hotel)
        return hotel_data_model
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel data model": {"message": "data does not exists"}})


def predefined_rate_exists(id, hotel):
    try:
        predefined_rate = hotel_models.PredefinedRate.objects.get(id=id, hotel=hotel)
        return predefined_rate
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"predefined rate": {"message": "data does not exists"}})


def predefined_rate_exists_and_not_order_1(id, hotel):
    predefined_rate = predefined_rate_exists(id, hotel)
    if predefined_rate.order > 1:
        return predefined_rate
    else:
        raise serializers.ValidationError({"predefined rate": {"message": "predefined already in top"}})


def booking_prop_exists(id, hotel):
    try:
        booking_prop = hotel_models.BookingProp.objects.get(id=id, hotel=hotel)
        return booking_prop
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"booking prop": {"message": "data does not exists"}})


def competitor_exists(id, hotel):
    try:
        competitor = hotel_models.Competitor.objects.get(id=id, client_hotel=hotel)
        return competitor
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"competitor": {"message": "competitor does not exists"}})


def inventory_exists(id, hotel):
    try:
        inventory = hotel_models.Inventory.objects.get(id=id, hotel=hotel)
        return inventory
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"inventory": {"message": "inventory does not exists"}})


def client_subscription_hotel_exists(subscription_id, message="subscription hotel does not exists"):
    try:
        hotel = hotel_models.ClientHotel.objects.get(subscription_id=subscription_id)
        return hotel
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": message}})

def time_to_booking_adjustment_exists(hotel, message="time to booking adjusment data does not exists"):
    try:
        time_to_booking_adjustment = hotel_models.TimeToBookingAdjustment.objects.get(hotel=hotel)
        return time_to_booking_adjustment
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"hotel": {"message": message}})

def unused_competitor_list(id):
    try:
        competitor = hotel_models.CompetitorHotelList.objects.get(id = id)
        competitor_used = hotel_models.Competitor.objects.filter(competitor = competitor)
        if competitor_used.exists():
            raise serializers.ValidationError({"competitor_list": {"message": "competitor list is used by client hotel"}})
        else:
            return competitor
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"competitor_list": {"message": "competitor list doesn't exists"}})

def price_note_exists(id,hotel):
    try:
        price_note = hotel_models.PriceNote.objects.get(id = id,hotel = hotel)
        return price_note
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"price note": {"message": "price note data doesn't exists"}})

def feature_exists(id):
    try:
        feature = hotel_models.Feature.objects.get(id = id)
        return feature
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"Feature": {"message": "feature doesn't exists"}})