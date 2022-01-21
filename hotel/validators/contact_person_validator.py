from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hotel import models as hotel_models


def contact_person_exists(id, hotel):
    try:
        contact_person = hotel_models.ContactPerson.objects.get(id=id, hotel=hotel)
        return contact_person
    except ObjectDoesNotExist:
        raise serializers.ValidationError({"contact_person": {"message": "contact person does not exists"}})
