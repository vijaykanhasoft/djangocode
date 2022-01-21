from rest_framework import permissions

from account import models as account_models
from hotel.validators import hotel_validator
from system.validators import request_validator
from django.conf import settings


class ProHotel(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.auth.hotel.is_pro

class InngeniusHotel(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.auth.hotel.pms_is_inngenius
