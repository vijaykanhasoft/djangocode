# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from hotel import models as hotel_models


# Register your models here.

class HotelOTAAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'address',
        'region',
        'postcode',
        'country',
        'review',
        'platform'
    )
    list_filter = (
        'country',
        'platform',
    )


class HotelMappingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_com_hotel',
        'hotels_com_hotel',
    )


class ClientHotelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'state',
        'monthly_bill',
        'number_of_rooms',
        'predefined_rate',
        'all_room_pricing',
        'client'
    )
    list_filter = (
        'state',
        'client',
    )


class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'max_occupancy',
        'hotel',
    )
    list_filter = (
        'hotel',
    )


class ClientRoomInformationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'max_occupancy',
        'avg_price',
        'min_price',
        'max_price',
        'pms_room',
        'pms_rate',
        'is_reference_room',
        'variable_cost_per_room',
        'breakfast_per_person',
        'breakfast',
        'hotel',

    )
    list_filter = (
        'hotel',
    )



admin.site.register(hotel_models.HotelOTA, HotelOTAAdmin)
admin.site.register(hotel_models.HotelMapping, HotelMappingAdmin)
admin.site.register(hotel_models.ClientHotel, ClientHotelAdmin)
admin.site.register(hotel_models.Room, RoomAdmin)
admin.site.register(hotel_models.ClientRoomInformation, ClientRoomInformationAdmin)

