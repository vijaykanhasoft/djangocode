from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hotel import models as hotel_models


def individual_date_adjustment_exists(id, hotel):
    try:
        individual_date_adjustment = hotel_models.IndividualDateAdjustment.objects.get(id=id, hotel=hotel)
        return individual_date_adjustment
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"individual date adjustment": {"message": "data does not exists"}})


def daily_adjustment_exists(id, hotel):
    try:
        daily_adjustment = hotel_models.DailyAdjustment.objects.get(id=id, hotel=hotel)
        return daily_adjustment
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"daily adjustment": {"message": "data does not exists"}})


def monthly_adjustment_exists(id, hotel):
    try:
        monthly_adjustment = hotel_models.MonthlyAdjustment.objects.get(id=id, hotel=hotel)
        return monthly_adjustment
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"monthly adjustment": {"message": "data does not exists"}})


def skip_pricing_exists(id, hotel):
    try:
        skip_pricing = hotel_models.SkipPricing.objects.get(id=id, hotel=hotel)
        return skip_pricing
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"skip pricing": {"message": "data does not exists"}})
