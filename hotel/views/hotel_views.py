import datetime
import json

import chargebee
from django.conf import settings
from rest_framework import filters
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from account import permissions as account_permission
from account.validators import user_validator
from hotel import models as hotel_models
from hotel.helpers import hotel_helper
from hotel.helpers import room_helper
from hotel.serializers import hotel_serializer
from hotel.validators import hotel_validator
from rest_framework.decorators import api_view, permission_classes
import os
from django.http import HttpResponse
from system.validators import request_validator
from rest_framework.views import APIView
from hotel.helpers import algorithm_setting
from hotel.helpers import file as hotel_file_helpers
from django.core.cache import cache
from pricing_algorithm.helpers import price_history as price_history_helper , algo_tasks as algo_task_helper
from pricing_algorithm.helpers import price_cache as price_cache_helper
from hotel.helpers import algorithm_setting
from rest_framework import serializers
from hotel.helpers import algorithm_setting as algorithm_settings_helper


class HotelList(generics.ListAPIView):
    serializer_class = hotel_serializer.HotelSerializer
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','address','country__name','country__abbreviation','postcode','region','currency__name','currency__abbreviation']

    def get_queryset(self):
        auth = self.request.auth

        _country_filter = self.request.GET.get("country")
        if _country_filter is None:
            raise serializers.ValidationError({"payload": {"message": "country is required"}})
        qs = self.filter_queryset(hotel_models.HotelOTA.objects.all())
        if auth.is_hotel_token:
            hotel = auth.hotel
            qs = qs.filter(country=hotel.country)
            hotel_list_id = qs.values_list("id",flat=True)
            return hotel_models.HotelOTA.objects.filter(pk__in=hotel_list_id).extra(select={
            'distance': " select (6371.1 * 2 * asin(sqrt(power(sin((radians(%s) - radians(cast(lat as decimal))) / 2), 2) + cos(radians(%s) ) * cos( radians(cast(lat as decimal)) ) * power(sin( (radians(%s) - radians( cast(lng as decimal)) ) / 2), 2) ) ))"},
            select_params=(
                str(hotel.lat), str(hotel.lat),
                str(hotel.lng),), ).order_by(
            'distance')

        qs = qs.filter(country_id=_country_filter).order_by("name")
        return qs


class ClientHotelDetail(generics.RetrieveAPIView):
    serializer_class = hotel_serializer.ClientHotelSerializer
    permission_classes = (IsAuthenticated, account_permission.HotelToken, account_permission.AdminOrHotelStaff)

    def get_object(self):
        return self.request.auth.hotel


class ClientHotelList(generics.ListAPIView):
    serializer_class = hotel_serializer.ClientHotelSerializer
    permission_classes = (IsAuthenticated, account_permission.AdminOrReseller,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'country__name', 'country__abbreviation', 'postcode', 'region',
                     'currency__name', 'currency__abbreviation','client__email','state','id']
    ordering_fields = ('name', 'address', 'country__name', 'country__abbreviation', 'postcode', 'region',
                     'currency__name', 'currency__abbreviation','client__email','state','id','pms__provider','last_update_price_pms','last_run_pricing','last_update_price_pms_status','is_update_to_pms','last_login')

    def get_queryset(self):

        basic_qs = hotel_models.ClientHotel.objects.all().extra(
            select={'last_login': 'select last_login from hotel_analytic where hotel_id = "hotel_clienthotel"."id"'}
        )

        qs = self.filter_queryset(basic_qs)

        provider_filter = self.request.GET.get("pms_provider")
        if provider_filter is not None:
            qs = qs.filter(pms__provider = provider_filter)
        auth = self.request.auth

        if auth.reseller is not None:
            qs = qs.filter(reseller = auth.reseller)

        return qs



class HotelRegister(generics.CreateAPIView):
    serializer_class = hotel_serializer.ClientHotelSerializer
    permission_classes = (IsAuthenticated, account_permission.Admin,)


class HotelUpdate(generics.UpdateAPIView):
    serializer_class = hotel_serializer.ClientHotelSerializer
    permission_classes = (IsAuthenticated, account_permission.HotelToken, account_permission.AdminOrHotelStaff,)

    def get_object(self):
        return self.request.auth.hotel

class HotelUpdatePmsSync(APIView):
    permission_classes = (IsAuthenticated, account_permission.HotelToken, account_permission.AdminOrHotelStaff,)
    def post(self,request):
        request_validator.parameter_exists(request,"pms_sync")
        hotel = hotel_models.ClientHotel.objects.get(id = request.auth.hotel.id)
        hotel.pms_sync = request.data.get("pms_sync")
        hotel.save()
        serializer = hotel_serializer.ClientHotelSerializer(hotel)
        return Response(serializer.data)



class UpdateFreeTrialEnd(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.Admin, account_permission.HotelToken,)

    def post(self, request):
        today =datetime.date.today()
        hotel = request.auth.hotel
        client = hotel.client

        request_validator.parameter_is_type(request,"free_trial_end",str,True)
        client.free_trial_end = datetime.datetime.strptime(request.data.get("free_trial_end"),'%Y-%m-%d').date()
        client_hotel_state = None
        if client.free_trial_end >= today:
            client_hotel_state = 0
        else:
            client_hotel_state = 3
        client.save()
        client_hotels = hotel_models.ClientHotel.objects.filter(client = client,state__in = [0,3])
        for _hotel in client_hotels:
            _hotel.state = client_hotel_state
            _hotel.save()

            _str_hotel_id = str(_hotel.id)
            if client_hotel_state == 0:
                algo_task_helper.re_register_algo_program(_str_hotel_id)

        return Response(status=status.HTTP_200_OK, data=hotel_serializer.ClientHotelSerializer(hotel, many=False).data)


class UpdateMonthlyBill(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.Admin, account_permission.HotelToken,)

    def post(self,request):
        hotel = request.auth.hotel
        request_validator.parameter_is_types(request,"monthly_bill",[float,int],True)
        hotel.monthly_bill = request.data.get("monthly_bill")
        hotel.using_override_bill = True
        hotel.save()
        if hotel.subscription_id is not None:
            hotel_subscription_hp = hotel_helper.HotelSubscriptionHelper(hotel)
            hotel_subscription_hp.update_subscription()



        return Response(status=status.HTTP_200_OK, data=hotel_serializer.ClientHotelSerializer(hotel, many=False).data)

    def put(self,request):
        hotel = request.auth.hotel
        hotel_subscription_hp = hotel_helper.HotelSubscriptionHelper(hotel)
        subscription_data = hotel_subscription_hp.subscription()
        monthly_bill = float(subscription_data["subscription"]["plan_unit_price"]) / 100.0
        if subscription_data["subscription"]["plan_quantity"] > 1:
            monthly_bill = monthly_bill * subscription_data["subscription"]["plan_quantity"]
        hotel.monthly_bill = monthly_bill
        hotel.using_override_bill = False
        hotel.save()
        if hotel.subscription_id is not None:
            hotel_subscription_hp.update_subscription()


        return Response(status=status.HTTP_200_OK,data=hotel_serializer.ClientHotelSerializer(hotel,many=False).data)




class LinkHotelToClient(generics.GenericAPIView):
    serializer_class = hotel_serializer.LinkHotelToClientSerializer
    permission_classes = (IsAuthenticated, account_permission.AdminOrReseller,)



    def post(self, request):

        auth = request.auth
        user = auth.user

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid()

        request_validator.parameter_is_type(request,"client",int)
        request_validator.parameter_is_type(request, "hotel", int)
        request_validator.parameter_is_type(request, "currency", int)

        client = user_validator.owner_account(request.data.get("client"))

        original_hotel = hotel_validator.hotel_exists(request.data.get("hotel"))

        client_hotel_hp = hotel_helper.ClientHotelHelper(original_hotel=original_hotel,
                                                         number_of_rooms=request.data.get("number_of_rooms"),
                                                         currency=serializer.validated_data["currency"],
                                                         client=client,
                                                         )

        hotel = client_hotel_hp.client_hotel
        hotel.client = client
        hotel.reseller = serializer.validated_data.get("reseller")
        hotel.responsible_person_id = request.data.get("responsible_person")


        if hotel.reseller_hotel:
            hotel.state = 6

        # hotel.free_trial_end = datetime.date.today() + datetime.timedelta(days=30)
        hotel.save()

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

        #time to booking adjustment
        hotel_setup_helper.set_time_to_booking_adjustment()

        #set inngenius folder path
        hotel_setup_helper.set_inngenius_folder_path()

        #set monthly bill
        hotel_subscription_hp = hotel_helper.HotelSubscriptionHelper(hotel)
        subscription_data = hotel_subscription_hp.subscription()
        monthly_bill = float(subscription_data["subscription"]["plan_unit_price"]) / 100.0
        if subscription_data["subscription"]["plan_quantity"] > 1:
            monthly_bill = monthly_bill * subscription_data["subscription"]["plan_quantity"]
        hotel.monthly_bill = monthly_bill
        hotel.save()

        algorithm_hp = algorithm_setting.AlgorithmSetting(hotel)
        algorithm_data = algorithm_hp.set_default_settings()
        algorithm_hp.write_data_to_table(algorithm_data)

        return Response(status=status.HTTP_201_CREATED)

class SmartSettings(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, account_permission.HotelToken, account_permission.AdminOrHotelStaff,)
    serializer_class = hotel_serializer.SmartDateSettingsSerializer

    def get_object(self):
        return self.request.auth.hotel

class CalculateDateSetting(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.HotelToken, account_permission.AdminOrHotelStaff,)

    def post(self, request):
        hotel = request.auth.hotel
        start_date = datetime.date.today()
        end_date = request.data.get("end_date")

        if not request.data.get("end_date"):
            after_one_year_date = start_date + datetime.timedelta(days=365)
            end_date = after_one_year_date - datetime.timedelta(days=after_one_year_date.day)

        serialized_data = hotel_serializer.CalculateDateSettingSerializer(instance={"hotel":hotel, "start_date": str(start_date), "end_date": str(end_date)}).data

        return Response(serialized_data, status=status.HTTP_200_OK)

class Checkout(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.HotelToken ,account_permission.AdminOrHotelStaff,)

    def post(self, request):
        hotel = request.auth.hotel
        client = hotel.client
        hotel_subscription_hp = hotel_helper.HotelSubscriptionHelper(hotel)

        hosted_page_data = {
            "customer": {
                "email": client.email,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "taxability": "taxable",
                "company": hotel.name,
            },
            "billing_address": {
                "first_name": client.first_name,
                "last_name": client.last_name,
            },
            "card": {
                "gateway_account_id": settings.CHARGEBEE_GATEWAY_ID
            }

        }
        subscription_data = hotel_subscription_hp.hotel_subscription
        if subscription_data["subscription"] is not None:
            subscription_data["subscription"]["plan_unit_price"] = int(subscription_data["subscription"]["plan_unit_price"])
            hosted_page_data["subscription"] = subscription_data["subscription"]
        result = chargebee.HostedPage.checkout_new(hosted_page_data)
        hosted_page = result._response['hosted_page']
        return Response(hosted_page)


class Portal(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.HotelToken ,account_permission.AdminOrHotelStaff,)

    def post(self, request, format=None):
        hotel = request.auth.hotel
        client = hotel.client

        result = chargebee.PortalSession.create({
            "customer": {
                "id": hotel.subscription_id,
            }
        })
        portal_session = result._response['portal_session']
        return Response(portal_session)


class CustomserLink(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)

    def post(self, request, format=None):
        hotel = request.auth.hotel
        client = hotel.client
        result = chargebee.HostedPage.retrieve(request.data["hosted_page_token"])
        hosted_page = result.hosted_page
        if hosted_page.type == "checkout_new":
            if hotel.state == 0:
                hotel.state = 1
            hotel.expiry_date = datetime.datetime.fromtimestamp(
                hosted_page.content.subscription.next_billing_at).date() + datetime.timedelta(days=7)
            hotel.next_charge = datetime.datetime.fromtimestamp(hosted_page.content.subscription.next_billing_at).date()
            monthly_bill = 0
            if hosted_page.content.subscription.addons is not None:
                for addon in hosted_page.content.subscription.addons:
                    monthly_bill += (addon.unit_price * addon.quantity)
            monthly_bill += (
                        hosted_page.content.subscription.plan_unit_price * hosted_page.content.subscription.plan_quantity)
            hotel.monthly_bill = float(monthly_bill) / float(100)
            hotel.subscription_id = hosted_page.content.subscription.id
            hotel.save()
        client_id = hosted_page.content.customer.id
        # if client.payment_account_id is None:
        #     client.payment_account_id = client_id
        #     client.save()
        return Response(hotel_serializer.ClientHotelSerializer(hotel, many=False).data)


class ScrapeList(generics.ListAPIView):
    serializer_class = hotel_serializer.CompetitorListSerializer
    permission_classes = (IsAuthenticated, account_permission.Admin,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['__all__']

    def get_queryset(self):
        competitors = hotel_models.CompetitorHotelList.objects.all()
        return competitors

class ScrapeListDelete(generics.DestroyAPIView):
    serializer_class = hotel_serializer.CompetitorListSerializer
    permission_classes = (IsAuthenticated, account_permission.Admin,)

    def get_object(self):
        return hotel_validator.unused_competitor_list(self.kwargs.get("id"))




@api_view(['GET'])
@permission_classes((account_permission.DownloadDiagnosticFile, ))
def download_diagnostic_file(request,diagnostic_id):
    auth = request.auth
    hotel = auth.hotel
    file_path = settings.DIAGNOSTIC_FILE_PATH+diagnostic_id+".csv"
    if os.path.isfile(file_path):
        diagnostic_file = open(file_path, "rb").read()
        resp =  HttpResponse(diagnostic_file, content_type="text/csv")
        str_current_time = str(datetime.datetime.now().date())
        resp['Content-Disposition'] = 'attachment; filename=diagnostic-'+hotel.name+"-"+str_current_time+".csv"
        return resp
    else:
        content = {
            'diagnostic_File': "file doesn't exists"
        }
        return Response(content)

@api_view(['GET'])
@permission_classes((account_permission.DownloadReservationFile, ))
def download_reservation_file(request, reservation_id):
    auth = request.auth
    hotel = auth.hotel
    file_path = settings.BOOKING_SUITE_FILE_PATH+str(hotel.id)+"/"+reservation_id+".csv"
    if os.path.isfile(file_path):
        reservation_file = open(file_path, "rb").read()
        resp =  HttpResponse(reservation_file, content_type="text/csv")
        str_current_time = str(datetime.datetime.now().date())
        resp['Content-Disposition'] = 'attachment; filename=reservation_'+str(hotel.id)+reservation_id+str_current_time+".csv"
        return resp
    else:
        content = {
            'reservation_File': "file doesn't exists"
        }
        return Response(content)

@api_view(['GET'])
@permission_classes((account_permission.DownloadInngeniusFile, ))
def download_inngenius_file(request,download_id):
    auth = request.auth
    hotel = auth.hotel
    file_path = hotel.inngenius_folder_path+download_id+".csv"
    if os.path.isfile(file_path):
        diagnostic_file = open(file_path, "rb").read()
        resp =  HttpResponse(diagnostic_file, content_type="text/csv")
        str_current_time = str(datetime.datetime.now().date())
        resp['Content-Disposition'] = 'attachment; filename=inngenius_'+str_current_time+".csv"
        return resp
    else:
        content = {
            'inngenius_file': "file doesn't exists"
        }
        return Response(content)




@api_view(['GET'])
@permission_classes((account_permission.DownloadClientListFile, ))
def download_client_list(request):
    file_path = hotel_file_helpers.write_client_list_csv()
    if os.path.isfile(file_path):
        client_list_file = open(file_path, "rb").read()
        resp =  HttpResponse(client_list_file, content_type="text/csv")
        str_current_time = str(datetime.datetime.now().date())
        resp['Content-Disposition'] = 'attachment; filename=client-list-'+str_current_time+".csv"
        return resp
    else:
        content = {
            'client_list_file': "file doesn't exists"
        }
        return Response(content)


class GetLastUpdateAndPricing(APIView):
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)

    def get(self,request):
        auth = request.auth
        hotel =  auth.hotel

        # cached_price = cache.get("pricing-" + str(hotel.id))
        price_cache_hp = price_cache_helper.PriceCache(hotel)
        cached_price = price_cache_hp.price_cache

        result = {}

        if "last_pricing" in cached_price:
            result["last_pricing"] = cached_price.get("last_pricing")
        if "last_update" in cached_price:
            result["last_update"] = cached_price.get("last_update")
        if "last_update_result" in cached_price:
            result["last_update_result"] = cached_price.get("last_update_result")
        if "update_status" in cached_price:
            result["update_status"] = cached_price.get("update_status")

        return Response(status=status.HTTP_200_OK, data=result)

    def post(self,request):
        auth = request.auth
        hotel = auth.hotel
        current_time = datetime.datetime.now()
        hotel.last_run_pricing_type = request.data.get("last_run_pricing_type")
        hotel.last_run_pricing = current_time
        hotel.save()



        return Response(status=status.HTTP_200_OK,data = {"current_time":current_time,"last_run_pricing":hotel.last_run_pricing})

class GetPricingHistoryDate(APIView):
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)

    def get(self,request):
        auth = request.auth
        hotel =  auth.hotel

        settings_data = algorithm_settings_helper.AlgorithmSetting(hotel)
        algo_setting_data = settings_data.algo_setting_data
        _hotel_object = algo_setting_data.get("hotel")

        price_history_hp = price_history_helper.PriceHistoryHelper(_hotel_object)

        return Response(status=status.HTTP_200_OK, data=price_history_hp.save_dates)

class GetPricingHistory(APIView):
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)

    def get(self,request):
        auth = request.auth
        hotel =  auth.hotel
        date = request.GET.get("date")

        settings_data = algorithm_settings_helper.AlgorithmSetting(hotel)
        algo_setting_data = settings_data.algo_setting_data
        _hotel_object = algo_setting_data.get("hotel")

        price_history_hp = price_history_helper.PriceHistoryHelper(_hotel_object)

        data = price_history_hp.get_price_data(date)

        if data is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_200_OK, data=data)

class FeatureFlag(APIView):
    permission_classes = (IsAuthenticated, account_permission.AdminOrHotelStaff,)

    def get(self,request):
        auth = request.auth
        hotel =  auth.hotel
        data = hotel_serializer.FeatureSerializer(hotel.features.all(),many=True).data

        return Response(status=status.HTTP_200_OK, data=data)

    def post(self,request):
        auth = request.auth
        hotel = auth.hotel

        feature = hotel_validator.feature_exists(request.data.get("id"))

        if feature in hotel.features.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"message":"feature already enabled"})

        hotel.features.add(feature)
        hotel.save()

        data = hotel_serializer.FeatureSerializer(hotel.features.all(), many=True).data

        return Response(status=status.HTTP_200_OK, data=data)

    def delete(self, request,id):
        auth = request.auth
        hotel = auth.hotel

        feature = hotel_validator.feature_exists(id)

        if feature not in hotel.features.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"message": "feature already disabled"})

        hotel.features.remove(feature)
        hotel.save()

        data = hotel_serializer.FeatureSerializer(hotel.features.all(), many=True).data

        return Response(status=status.HTTP_200_OK, data=data)


