import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from account.validators import user_validator
from hotel import models as hotel_models
from pricing_algorithm import models as pricing_algorithm_models
from hotel.validators import hotel_validator
from system.serializers import country_serializer
from system.serializers import currency_serializer
from pricing_algorithm.serializers import algo_program_serializer
from system.validators import request_validator, data_validator

from hotel.helpers import inventory_helper
from hotel.helpers import hotel_helper
from hotel.helpers import room_helper
import json
from hotel.serializers import daily_adjustment_serializer,monthly_adjustment_serializer
import numpy as np
from system.validators import data_validator as system_validator
from hotel.helpers import algorithm_setting
from account.serializers import user_serializer, reseller_serializer
from account.helpers import reseller_helper
from account.validators import reseller_validator

class HotelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('exclude_fields', None)
        super(HotelSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)

    country = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    competitor_data = serializers.SerializerMethodField()
    # distance = serializers.SerializerMethodField()

    class Meta:
        model = hotel_models.HotelOTA
        fields = (
            "id",
            "lat",
            "lng",
            "address",
            "region",
            "postcode",
            "country",
            "currency",
            "name",
            "ota_reference",
            "website",
            "review",
            "competitor_data",
            # "distance",
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'scrape_data': {'read_only': True},

        }

    # def get_scrape_data(self, obj):
    #     as_competitor_data = hotel_models.CompetitorHotelList.objects.filter(hotel = obj)
    #     if as_competitor_data.exists():
    #         as_competitor_data = as_competitor_data.first()
    #         return CompetitorListSerializer(as_competitor_data,many=False,exclude_fields=["id","hotel"]).data
    #     return None
    # def get_distance(self, obj):
    #     return obj.distance

    def get_country(self, obj):
        if obj.country is None:
            return None
        return country_serializer.CountrySerializer(obj.country, many=False).data

    def get_currency(self, obj):
        if obj.currency is None:
            return None
        return currency_serializer.CurrencySerializer(obj.currency, many=False).data

    def get_competitor_data(self, obj):
        try:
            competitor = hotel_models.CompetitorHotelList.objects.get(hotel=obj) 
            return CompetitorListSerializer(competitor, many=False, exclude_fields=["hotel", ]).data
        except ObjectDoesNotExist:
            return None


class ClientHotelSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    pms_provider = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    free_trial_end = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    responsible_person = serializers.SerializerMethodField()
    reseller = serializers.SerializerMethodField()

    def validate(self, attrs):
        request = self.context['request']

        auth = request.auth
        user = auth.user
        reseller = auth.reseller

        if request.method == "POST":
            request_validator.parameter_is_type(request, "client",int)
            user_validator.user_exists({"id":request.data.get("client"),"is_staff":False})

            request_validator.parameter_exists(request, "responsible_person")
            responseible_user_id = request.data.get("responsible_person")

            if user.is_staff:
                reseller_id = request.data.get("reseller")
                if reseller_id is not None:
                    reseller = reseller_validator.reseller_exists(reseller_id)

            if reseller is not None:
                if not reseller_helper.get_reseller_access_responseible_user(responseible_user_id, reseller):
                    raise serializers.ValidationError(
                        {"manager": {"message": "responsible user is not part of " + reseller.name}})
            else:
                responsible_user = user_validator.user_exists({"id": responseible_user_id})
                if not responsible_user.is_staff:
                    raise serializers.ValidationError(
                        {"responsible person": {"message": "responsible user need to be RPG admin/sales team "}})

        if "country" in request.data:
            system_validator.country_exists(request.data.get("country"))

        return attrs

    class Meta:
        model = hotel_models.ClientHotel
        extra_kwargs = {
            'client': {'read_only': True},
            'id': {'read_only': True},
            'pms_sync': {'read_only': True},
            'is_using_smart_settings': {'read_only': True},
            'pms': {'read_only': True},
            'subscription_id': {'read_only': True},
            'free_trial_end': {'read_only': True},
            'using_override_bill': {'read_only': True},
            'monthly_bill': {'read_only': True},
            'expiry_date': {'read_only': True},
            'next_charge': {'read_only': True},
            'show_free_trial_date_in_expired': {'read_only': True},
            'is_pro': {'read_only': True},
            'pms_provider': {'read_only': True},
            'email': {'read_only': True},
            'state': {'read_only': True},
            'is_update_to_pms': {'read_only': True},
            'update_to_pms_type' : {'read_only': True},
            'update_to_pms_skip_type':{'read_only':True},
            'timezone': {'read_only': True},
            'min_price': {'read_only': True},
            'algo_task_info':{'read_only':True},
            'last_update_price_pms': {'read_only': True},
            # 'last_run_pricing': {'read_only': True},
            'last_update_price_pms_result': {'read_only': True},
            'last_update_price_pms_status': {'read_only': True},
            'last_inventory_price_get': {'read_only': True},
            'last_run_pricing_type': {'read_only': True},

        }
        fields = (
            "id",
            "lat",
            "lng",
            "currency",
            "address",
            "region",
            "postcode",
            "country",
            "name",
            "pms_sync",
            "pms",
            "website",
            "review",
            "notes",
            "client",
            "all_room_pricing",
            "predefined_rate",
            "number_of_rooms",
            'subscription_id',
            'free_trial_end',
            'using_override_bill',
            'monthly_bill',
            'expiry_date',
            'next_charge',
            'show_free_trial_date_in_expired',
            "is_pro",
            "pms_provider",
            "email",
            "is_locked",
            "state",
            "is_update_to_pms",
            "update_to_pms_type",
            "update_to_pms_skip_type",
            "timezone",
            "is_using_smart_settings",
            "last_login",
            'last_update_price_pms',
            'last_run_pricing',
            'last_update_price_pms_result',
            'last_update_price_pms_status',
            'last_inventory_price_get',
            'min_price',
            'booking_suite_hotel_id',
            'last_run_pricing_type',
            'booking_suite_hotel_connection',
            'target_occupancy',
            'responsible_person',
            'reseller',
        )

    def get_reseller(self,instance):
        if instance.reseller is not None:
            return reseller_serializer.ResellerSerializer(instance.reseller,many=False).data
        return None
    def get_responsible_person(self,instance):
        if instance.responsible_person is not None:
            return user_serializer.UserLiteSerializer(instance.responsible_person,many=False).data
        return None

    def get_last_login(self,obj):
        try:
            analytic_data = hotel_models.Analytic.objects.get(hotel = obj)
            return analytic_data.last_login
        except:
            return None

    def get_free_trial_end(self,obj):
        return obj.client.free_trial_end
    def get_is_locked(self,obj):
        today = datetime.date.today()
        if obj.state == 0:
            return obj.client.free_trial_end < today
        elif obj.state == 6:
            return False
        elif obj.state == 7 or obj.state == 2 or obj.state == 4 or obj.state == 5:
            return True
        try:
            return obj.expiry_date < today
        except:
            return True
    def get_email(self,obj):
        return obj.client.email
    def get_pms_provider(self,obj):
        if obj.is_pms_linked:
            return obj.pms.provider
        return None

    def get_country(self, obj):
        if obj.country is None:
            return None
        return country_serializer.CountrySerializer(obj.country, many=False).data

    def get_currency(self, obj):
        if obj.currency is None:
            return None
        return currency_serializer.CurrencySerializer(obj.currency, many=False).data

    def get_algo_task_info(self,obj):
        res = pricing_algorithm_models.AlgoTasks.objects.filter(hotel_id=obj,status__in=(3,4)).order_by('-id')
        if len(res)>0:
            return algo_program_serializer.AlgoProgramExecuteSerializer(res.first(),exclude_fields=["id","program_name","program_id","task","status","created","task_url","is_update_to_pms","update_result", ]).data

    def setup_hotel_property(self,request,hotel,validated_data):


        auth = request.auth

        # ref room creation
        reference_room_data = json.loads(request.data.get("reference_room_data"))
        reference_room_data["is_reference_room"] = True
        reference_room_data["min_price"] = 99
        reference_room_data["max_price"] = 101
        reference_room_data["variable_cost_per_room"] = 0
        room_hp = room_helper.RoomHelper(reference_room_data, hotel)
        reference_room = room_hp.room

        hotel_setup_helper = hotel_helper.HotelHelper(hotel)
        hotel_setup_helper.set_new_reference_room(reference_room.id)
        hotel_setup_helper.set_reference_room()

        # hotel adjustment
        hotel_setup_helper.set_monthly_adjustment()
        hotel_setup_helper.set_daily_adjustment()

        # hotel data model
        hotel_setup_helper.set_hotel_data_model()

        # expected occupancy
        hotel_setup_helper.set_expected_occupancy()

        # competitors
        hotel_setup_helper.set_competitors()

        # booking prop
        hotel_setup_helper.set_booking_props()

        # time to booking adjustment
        hotel_setup_helper.set_time_to_booking_adjustment()

        # set inngenius folder path
        hotel_setup_helper.set_inngenius_folder_path()

        # set monthly bill
        hotel_subscription_hp = hotel_helper.HotelSubscriptionHelper(hotel)
        subscription_data = hotel_subscription_hp.subscription()
        monthly_bill = float(subscription_data["subscription"]["plan_unit_price"]) / 100.0
        if subscription_data["subscription"]["plan_quantity"] > 1:
            monthly_bill = monthly_bill * subscription_data["subscription"]["plan_quantity"]
        hotel.monthly_bill = monthly_bill

        hotel.reseller = validated_data.get("reseller")
        hotel.responsible_person_id = request.data.get("responsible_person")

        if hotel.reseller_hotel:
            hotel.state = 6


        hotel.save()

        algorithm_hp = algorithm_setting.AlgorithmSetting(hotel)
        algorithm_data = algorithm_hp.set_default_settings()
        algorithm_hp.write_data_to_table(algorithm_data)


    def create(self, validated_data):
        request = self.context['request']
        auth = request.auth
        user = request.auth.user

        # free_trial_end = datetime.date.today() + datetime.timedelta(days=30)
        hotel = hotel_models.ClientHotel.objects.create(
            currency_id=request.data.get("currency"),
            country_id=request.data.get("country"),
            client_id = request.data.get("client"),
            # free_trial_end=free_trial_end,
            timezone = request.data.get("timezone"),
            **validated_data
        )

        if user.is_reseller:
            hotel.reseller = auth.reseller
        else:
            hotel.responsible_person_id = request.data.get("responsible_person")

        if hotel.reseller_hotel:
            hotel.state = 6
        hotel.save()

        self.setup_hotel_property(request,hotel,validated_data)

        return hotel

    def update(self, instance, validated_data):
        request = self.context['request']

        for attr, value in request.data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LinkHotelToClientSerializer(serializers.Serializer):



    def validate(self, attrs):
        request = self.context['request']
        auth = request.auth
        user = auth.user

        reseller = auth.reseller

        request_validator.parameter_exists(request, "hotel")
        request_validator.parameter_exists(request, "reference_room_data")
        request_validator.parameter_exists(request, "client")
        request_validator.parameter_exists(request, "number_of_rooms")
        request_validator.parameter_exists(request, "currency")

        user_validator.owner_account(request.data.get("client"))

        hotel_validator.hotel_exists(request.data.get("hotel"))

        request_validator.parameter_exists(request, "responsible_person")
        responseible_user_id = request.data.get("responsible_person")

        if user.is_staff:
            reseller_id = request.data.get("reseller")
            if reseller_id is not None:
                reseller = reseller_validator.reseller_exists(reseller_id)

        if reseller is not None:
            if not reseller_helper.get_reseller_access_responseible_user(responseible_user_id,reseller):
                raise serializers.ValidationError({"manager": {"message": "responsible user is not part of "+reseller.name}})

        else:
            responsible_user = user_validator.user_exists({"id":responseible_user_id})
            if not responsible_user.is_staff:
                raise serializers.ValidationError(
                    {"responsible person": {"message": "responsible user need to be RPG admin/sales team "}})


        attrs["reseller"] = reseller
        attrs["currency"] = data_validator.currency_exists(request.data.get("currency"))
        return attrs


class HotelLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = hotel_models.HotelOTA
        fields = (
            "id",
            "name",
        )

class HotelClientLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = hotel_models.ClientHotel
        fields = (
            "id",
            "name",
        )

class CompetitorListSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('exclude_fields', None)
        super(CompetitorListSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            # for multiple fields in a list
            for field_name\
                    in remove_fields:
                self.fields.pop(field_name)

    hotel = serializers.SerializerMethodField()

    def get_hotel(self, obj):
        return HotelLiteSerializer(obj.hotel, many=False).data

    class Meta:
        model = hotel_models.CompetitorHotelList
        fields = (
            "id",
            "hotel",
            "max_price",
            "min_price",
            "avg_price",
            "number_of_price",
        )


class CompetitorSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('exclude_fields', None)
        super(CompetitorSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)

    competitor = serializers.SerializerMethodField()

    def get_competitor(self, obj):
        if obj.competitor is not None:
            CompetitorListSerializer(obj.competitor, many=False, exclude_fields=["id", ]).data
        return None

    class Meta:
        model = hotel_models.Competitor
        fields = (
            "id",
            "index",
            "competitor",
            "pricediff",
            "weight",
        )


class HotelWithCompetitorDataSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('exclude_fields', None)
        super(HotelWithCompetitorDataSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)

    competitor_data = serializers.SerializerMethodField()

    def get_competitor_data(self, obj):
        try:
            competitor = hotel_models.CompetitorHotelList.objects.get(hotel=obj)
            return CompetitorListSerializer(competitor, many=False, exclude_fields=["hotel", ]).data
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = hotel_models.HotelOTA
        fields = (
            "id",
            "name",
            "competitor_data",
        )
class SmartDateSettingsSerializer(serializers.ModelSerializer):
    daily_adjustment = serializers.SerializerMethodField()
    monthly_adjustment = serializers.SerializerMethodField()
    daily_competitor_average = serializers.SerializerMethodField()
    monthly_competitor_average = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()

    class Meta:
        model = hotel_models.ClientHotel
        fields = (
            'daily_adjustment',
            'monthly_adjustment',
            'daily_competitor_average',
            'monthly_competitor_average',
            'average_price'
        )

    def get_daily_adjustment(self,obj):
        daily_adjustment_data = hotel_models.DailyAdjustment.objects.filter(hotel = obj).order_by("day")
        return daily_adjustment_serializer.DailyAdjustmentSerializer(daily_adjustment_data,many=True).data

    def get_monthly_adjustment(self,obj):
        monthly_adjustment_data = hotel_models.MonthlyAdjustment.objects.filter(hotel=obj).order_by("month")
        return monthly_adjustment_serializer.MonthlyAdjustmentSerializer(monthly_adjustment_data, many=True).data

    def get_daily_competitor_average(self,obj):
        result = []
        rs = hotel_models.DailyWeightedAverage.objects.filter(hotel=obj)
        for i in range(1, 8):
            weighted_average_prices = rs.filter(date__week_day=i, date__gte=datetime.datetime.now().date()).values_list(
                "average_weighted")
            if weighted_average_prices.count() > 0:
                if i == 1:
                    result.append({"weekday": 7, "price_average": round(np.median(weighted_average_prices))})
                else:
                    result.append({"weekday": i - 1, "price_average": round(np.median(weighted_average_prices))})
            else:
                if i == 1:
                    result.append({"weekday": 7, "price_average": 0})
                else:
                    result.append({"weekday": i - 1, "price_average": 0})

        return result

    def get_monthly_competitor_average(self,obj):
        result = []
        rs = hotel_models.DailyWeightedAverage.objects.filter(hotel=obj)
        for i in range(1, 13):
            weighted_average_prices = rs.filter(date__month=i, date__gte=datetime.datetime.now().date()).values_list(
                "average_weighted")
            if weighted_average_prices.count() > 0:
                result.append({"month": i, "price_average": round(np.median(weighted_average_prices))})
            else:
                result.append({"month": i, "price_average": 0})

        return result

    def get_average_price(self,obj):
        reference_room = hotel_models.ClientRoomInformation.objects.get(hotel = obj,is_reference_room=True)
        return reference_room.avg_price

class FeatureSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('exclude_fields', None)
        super(FeatureSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = hotel_models.Feature
        fields = (
            "id",
            "name",
        )


