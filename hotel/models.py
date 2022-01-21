# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from hotel.helpers import pms_helper

DAYS = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),

)
MONTHS = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)


# Create your models here.
class HotelOTA(models.Model):
    PLATFOM_CHOICES = (
        (1, 'booking.com'),
        (2, 'hotels.com'),
        (3, 'expedia'),
    )
    lat = models.CharField(max_length=100, default=None, blank=True, null=True)
    lng = models.CharField(max_length=100, default=None, blank=True, null=True)
    address = models.TextField()
    region = models.CharField(max_length=200, null=True, blank=True, default=None)
    postcode = models.CharField(max_length=50, default=None, blank=True, null=True)
    country = models.ForeignKey("system.Country", to_field="id", related_name="hotel_region_id",
                                on_delete=models.CASCADE)
    currency = models.ForeignKey('system.Currency', to_field="id", related_name="hotel_ota_currency_id",
                                 on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=300)
    avg_price = models.FloatField(default=0)
    ota_reference = models.URLField(null=True, blank=True, default=None)
    website = models.URLField(null=True, blank=True, default=None)
    review = models.PositiveIntegerField()
    platform = models.PositiveSmallIntegerField(choices=PLATFOM_CHOICES, default=1)

    class Meta:
        verbose_name_plural = 'Hotel'

    def __str__(self):
        return self.name + "(" + str(self.id) + ")"


class HotelMapping(models.Model):
    booking_com_hotel = models.ForeignKey("hotel.HotelOTA", to_field="id",
                                          related_name="hotel_mapping_booking_com_hotel_id", on_delete=models.CASCADE)
    hotels_com_hotel = models.ForeignKey("hotel.HotelOTA", to_field="id",
                                         related_name="hotel_mapping_hotels_com_hotel_id", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Hotel Mapping'


class ClientHotel(models.Model):
    STATE_CHOICES = (
        (0, 'free trial'),
        (1, 'active'),
        (2, 'cancelled'),
        (3, 'free trial expired'),
        (4, 'suspended'),
        (5, 'not active'),
        (6, 'managed by reseller'),
        (7, 'locked by reseller'),
    )

    UPDATE_TYPE = (
        (1, '1 Week'),
        (2, '2 Week'),
        (3, '1 Month'),
        (4, '3 Month'),
        (5, '6 Month'),
        (6, '9 Month'),
        (7, 'Year'),
    )

    UPDATE_SKIP_TYPE = (
        (1, '1 Week'),
        (2, '2 Week')
    )

    RUN_PRICING_TYPE = (
        (1, '2 weeks'),
        (2, '1 month'),
        (3, '3 months'),
        (4, '6 months'),
        (5, '1 year')
    )

    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=0)
    lat = models.CharField(max_length=100, default=None, blank=True, null=True)
    lng = models.CharField(max_length=100, default=None, blank=True, null=True)
    currency = models.ForeignKey('system.Currency', to_field="id", related_name="hotel_currency_id",
                                 on_delete=models.CASCADE)
    address = models.TextField()
    region = models.CharField(max_length=200, null=True, blank=True, default=None)
    postcode = models.CharField(max_length=50, default=None, blank=True, null=True)
    country = models.ForeignKey("system.Country", to_field="id", related_name="hotel_client_region_id",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    pms_sync = models.PositiveSmallIntegerField(default=0)
    pms = models.ForeignKey("hotel.PMS", to_field="id", related_name="hotel_client_pms_id", null=True, blank=True,
                            default=None, on_delete=models.CASCADE)
    website = models.URLField(null=True, blank=True, default=None)
    review = models.PositiveIntegerField(default=0, blank=True)
    notes = models.TextField(null=True, blank=True, default=None)
    client = models.ForeignKey("account.User", to_field="id", related_name="hotel_client_client_client_id", on_delete=models.CASCADE)
    all_room_pricing = models.BooleanField(default=False)
    is_using_smart_settings = models.BooleanField(default=False)
    predefined_rate = models.BooleanField(default=False)
    number_of_rooms = models.PositiveIntegerField()
    subscription_id = models.CharField(max_length=200, null=True, blank=True, default=None)
    using_override_bill = models.BooleanField(default=False)
    # free_trial_end = models.DateField(null=True, blank=True, default=None)
    monthly_bill = models.FloatField(null=True, blank=True, default=None)
    expiry_date = models.DateField(null=True, blank=True, default=None)
    next_charge = models.DateField(null=True, blank=True, default=None)
    show_free_trial_date_in_expired = models.BooleanField(default=True)
    is_pro = models.BooleanField(default=False)
    booking_suite_hotel_id = models.CharField(max_length=15, null=True, blank=True, default=None)
    min_price = models.FloatField(default=0)
    hotel_reference = models.ForeignKey("hotel.HotelOTA", to_field="id", related_name="hotel_client_hotel_reference_id",
                                        on_delete=models.CASCADE, null=True, blank=True, default=None)
    is_update_to_pms = models.BooleanField(default=False)
    update_to_pms_type = models.IntegerField(choices=UPDATE_TYPE, blank=True, null=True)
    update_to_pms_skip_type = models.IntegerField(choices=UPDATE_SKIP_TYPE, blank=True, null=True)
    timezone = models.CharField(max_length=500, blank=True, null=True)
    last_update_price_pms = models.DateTimeField(null=True,blank=True,default=None)
    last_run_pricing = models.DateTimeField(null=True, blank=True,default=None)
    last_update_price_pms_result = models.TextField(null=True,blank=True,default=None)
    last_update_price_pms_status = models.BooleanField(default=False)
    last_inventory_price_get = models.DateTimeField(null=True, blank=True,default=None)
    last_run_pricing_type = models.PositiveSmallIntegerField(default=5, choices=RUN_PRICING_TYPE)
    created = models.DateField(auto_now=True,null=True,blank=True)
    booking_suite_hotel_connection = models.BooleanField(default=False)
    target_occupancy = models.FloatField(default=80)
    features = models.ManyToManyField("hotel.Feature")
    responsible_person = models.ForeignKey("account.User", to_field="id", related_name="hotel_client_hotel_account_user_id",
                                 null=True, blank=True, default=None, on_delete=models.CASCADE)
    reseller = models.ForeignKey("account.Reseller",to_field="id", related_name="hotel_client_hotel_reseller_id",
                                 null=True, blank=True, default=None, on_delete=models.CASCADE)


    class Meta:
        verbose_name_plural = 'Client Hotel'

    def __str__(self):
        return self.name + "(" + str(self.id) + ")"

    @property
    def reseller_hotel(self):
        return self.reseller is not None

    @property
    def is_room_dependent_pms(self):
        if self.is_pms_linked:
            if self.pms.provider == 8 or self.pms.provider == 17:
                return True 
              
    def last_update_price_pms_state(self):
        if self.last_update_price_pms is None:
            return None
        return self.last_update_price_pms_status


    @property
    def inngenius_folder_path(self):
        return settings.INNGENIUS_FILE_PATH+str(self.id)+'/'

    @property
    def inngenius_file_path(self):
        return self.inngenius_folder_path+"inngenius.csv"

    @property
    def bookingsuite_folder_path(self):
        return settings.BOOKING_SUITE_FILE_PATH+str(self.id)+'/'

    @property
    def is_pms_linked(self):
        return self.pms is not None

    @property
    def pms_is_independent_rate(self):
        if self.is_pms_linked:
            return self.pms.provider == pms_helper.MEWS
        return False
    @property
    def pms_is_inngenius(self):
        if self.is_pms_linked:
            return self.pms.provider == pms_helper.INNGENIUS
        return False
    @property
    def membership_state(self):
        if self.state == 0:
            return "free trial"
        elif self.state == 1:
            return "active"
        elif self.state == 2:
            return "canceled"
        elif self.state == 3:
            return "free trial expired"
        elif self.state == 4:
            return "suspended"
        elif self.state == 5:
            return "not active"
    @property
    def pms_provider(self):
        if self.pms is None:
            return "-"
        else:
            return self.pms.pms_provider




class Analytic(models.Model):
    hotel = models.OneToOneField("hotel.ClientHotel",to_field="id",related_name="hotel_analytic_client_hotel_id",on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True,blank=True,default=None)

    class Meta:
        verbose_name_plural = 'Analytic'




