# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import unittest
import datetime
import math
from rest_framework.test import APIClient
import shutil, os
import time
from account import models as account_models
from hotel import models as hotel_models
from system import models as system_models
from master import models as master_models
from rest_framework import status
from django.http import HttpResponsePermanentRedirect
from django.test.client import Client
from django.test import TestCase, RequestFactory
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import include, path, reverse
from django.utils import timezone
from hotel.validators import hotel_validator
from rpg_backend.helpers import test_case_helper
from datetime import timedelta

tc_helper = test_case_helper.TestCaseHelper()


from channels.testing import WebsocketCommunicator
from pricing_algorithm.consumer import SocketConsumer
from rpg_backend.routing import application
import asyncio
from django.conf import settings

import sys
import warnings
from rpg_backend.helpers import mongodb
mongo_helper = mongodb.MongoDB()
from collections import OrderedDict

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    
# There are two main functions of setup and tearDown
# In general term of test case will be executed like these
# 1) setUp
# 2) test
# 3) tearDown

# Test Class for Hotel
# Test Class for this API :- url(r'^list/$', hotel_views.HotelList.as_view()),

class HotelListTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')
   
    def test_hotel_list_invalid_url(self):
        self.client = APIClient()
        response = self.client.post('/hotel/list', format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/list/')

    def test_hotel_list_without_authorization(self):
        self.client = APIClient()
        response = self.client.get('/hotel/list/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_list_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/list/', format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_list_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        response = self.client.get('/hotel/list/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_list_with_correct_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/list/?country=6', format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()

# # Test Class for Client Hotel
# # Test Class for this API :- url(r'^client/list/$', hotel_views.ClientHotelList.as_view()),
class ClientHotelListTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')

        # Create Hotel 1
        hotel_data_1 = {'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','ota_reference':'https://www.abchotel.com','website':'','review':0}
        my_hotel_1 = tc_helper.create_hotelOTA(hotel_data_1)
        self.hotel_1 = my_hotel_1
        
        # Create ClientHotel
        client_hotel_data = {'state':0,'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','website':'https://www.abchotel.com','review':5,'pms_sync':0,'pms':None,'notes':'Test Notes','client':my_admin,'all_room_pricing':False,'predefined_rate':False,'number_of_rooms':5,'subscription_id':'JJhSoghRbkXr7IfWn','using_override_bill':False,'monthly_bill':None,'expiry_date':None,'next_charge':None,'show_free_trial_date_in_expired':True,'hotel_reference':my_hotel_1}
        my_client_hotel = tc_helper.create_ClientHotel(client_hotel_data)
        self.my_client_hotel = my_client_hotel 

    def test_client_hotel_list_invalid_url(self):
        self.client = APIClient()
        response = self.client.post('/hotel/client/list', format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/client/list/')

    def test_client_hotel_list_without_authorization(self):
        self.client = APIClient()
        response = self.client.get('/hotel/client/list/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_client_hotel_list_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/', format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_client_hotel_list_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        response = self.client.get('/hotel/client/list/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_client_hotel_list_with_correct_search_string(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/?search=hotel', format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_client_hotel_list_with_blank_search_string(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/?search=', format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_client_hotel_list_with_correct_sorting_desc(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/?ordering=-id', format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_client_hotel_list_with_wrong_sorting(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/?ordering=*id', format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_client_hotel_list_with_wrong_field_sorting(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/?ordering=-first_name', format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_client_hotel_list_with_correct_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/list/', format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()

# # Test Class for Client Hotel Detail
# # Test Class for this API :- url(r'^client/detail/$', hotel_views.ClientHotelDetail.as_view()),
class ClientHotelDetailTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')

        # Create Hotel 1
        hotel_data_1 = {'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','ota_reference':'https://www.abchotel.com','website':'','review':0}
        my_hotel_1 = tc_helper.create_hotelOTA(hotel_data_1)
        self.hotel_1 = my_hotel_1
        
        # Create ClientHotel
        client_hotel_data = {'state':0,'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','website':'https://www.abchotel.com','review':5,'pms_sync':0,'pms':None,'notes':'Test Notes','client':my_admin,'all_room_pricing':False,'predefined_rate':False,'number_of_rooms':5,'subscription_id':'JJhSoghRbkXr7IfWn','using_override_bill':False,'monthly_bill':None,'expiry_date':None,'next_charge':None,'show_free_trial_date_in_expired':True,'hotel_reference':my_hotel_1}
        my_client_hotel = tc_helper.create_ClientHotel(client_hotel_data)
        self.my_client_hotel = my_client_hotel

        # Client Hotel Token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post('/account/auth/hotel/'+str(self.my_client_hotel.id)+'/', format='json')
        self.hoteltoken = json.loads((response.content)).get('token')

    def test_client_hotel_detail_invalid_url(self):
        self.client = APIClient()
        response = self.client.post('/hotel/client/detail', format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/client/detail/')

    def test_client_hotel_detail_without_authorization(self):
        self.client = APIClient()
        response = self.client.get('/hotel/client/detail/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_client_hotel_detail_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        response = self.client.get('/hotel/client/detail/', format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_client_hotel_detail_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        response = self.client.get('/hotel/client/detail/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_client_hotel_detail_with_correct_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.hoteltoken)
        response = self.client.get('/hotel/client/detail/', format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()

# # Test Class for Hotel Register
# # Test Class for this API :- url(r'^register/$', hotel_views.HotelRegister.as_view()),
class HotelRegisterTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')
        self.admin = json.loads((response.content)).get('user')
        
        system_region = system_models.Region.objects.create(region='IN')
        self.region = system_region
        system_country=system_models.Country.objects.create(name='IN',abbreviation='in',region=system_region)
        self.country = system_country
        system_Currency = system_models.Currency.objects.create(name='Indian Rupee', abbreviation='INR', symbol='INR')
        self.currency = system_Currency
        
        # Create Aggressiveness
        aggre_data_1 = {'label':'Very Low','value':'-2','elasticity':'-12'}
        aggressive = tc_helper.create_Aggressiveness(aggre_data_1)
        self.aggressive = aggressive

        # Client Register
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'username':'kanhasoft@mail.com','password':'123456','first_name':'kanhasoft','last_name':'kanhasoft'}
        response = self.client.post('/account/client/register/',data, format='json')
        self.client_id = response.data.get('id')

        # Reseller Access    
        self.reseller, self.responsible_person = tc_helper.setResellerAccess()

    def test_hotel_register_invalid_url(self):
        self.client = APIClient()
        data = {}
        response = self.client.post('/hotel/register', data , format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/register/')

    def test_hotel_register_without_authorization(self):
        self.client = APIClient()
        data = {}
        response = self.client.post('/hotel/register/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_hotel_register_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        data = {}
        response = self.client.post('/hotel/register/', data, format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_register_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        data = {}
        response = self.client.post('/hotel/register/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_register_with_correct_key_authorization_with_wrong_key_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'na_me':'Hotel ABC','clie_nt':'ABC','address':'ABC 123'}
        response = self.client.post('/hotel/register/',data, format='json')
        name = json.loads((response.content)).get('name')
        country = json.loads((response.content)).get('country')
        address = json.loads((response.content)).get('address')
        client = json.loads((response.content)).get('client')
        review = json.loads((response.content)).get('review')
        number_of_rooms = json.loads((response.content)).get('number_of_rooms')
        statusflag = True
        if name is not None and name[0] == 'This field is required.':
            statusflag = False
        elif client is not None and client[0] == "client is required":
            statusflag = False
        elif address is not None and address[0] == "This field is required.":
            statusflag = False
        elif review is not None and review[0] == "This field is required.":
            statusflag = False
        elif number_of_rooms is not None and number_of_rooms[0] == "This field is required.":
            statusflag = False
        elif country is not None and country[0] == "This field is required.":
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_register_with_correct_key_authorization_with_blank_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'name':'','client':'','address':'ABC 123'}
        response = self.client.post('/hotel/register/',data, format='json')
        name = json.loads((response.content)).get('name')
        country = json.loads((response.content)).get('country')
        address = json.loads((response.content)).get('address')
        client = json.loads((response.content)).get('client')
        review = json.loads((response.content)).get('review')
        number_of_rooms = json.loads((response.content)).get('number_of_rooms')
        statusflag = True
        if name is not None and name[0] == 'This field is required.':
            statusflag = False
        elif client is not None and client[0] == "client is required":
            statusflag = False
        elif address is not None and address[0] == "This field is required.":
            statusflag = False
        elif review is not None and review[0] == "This field is required.":
            statusflag = False
        elif number_of_rooms is not None and number_of_rooms[0] == "This field is required.":
            statusflag = False
        elif country is not None and country[0] == "This field is required.":
            statusflag = False
        self.assertEquals(statusflag, False)  

    def test_hotel_register_with_correct_key_authorization_with_correct_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'state':0,'lat':'23.022505','lng':'72.57136209999999','address':'Ahmedabad, Gujarat, India','region':'xyz','postcode':'38004','country':str(self.country.id),'name':'ABC Hotel Kanhasoft','review':'15','client':self.client_id,'number_of_rooms':"10", 'currency':str(self.currency.id),'reference_room_data':json.dumps({"name": "Double Room", "max_occupancy": '2', "avg_price": '125'}),'reseller':self.reseller.id,'responsible_person':self.responsible_person.id}
        response = self.client.post('/hotel/register/',data, format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()

# # Test Class for Hotel Update
# # Test Class for this API :- url(r'^update/$', hotel_views.HotelUpdate.as_view()),
class HotelUpdateTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')
        self.admin = json.loads((response.content)).get('user')
        
        # Create Hotel 1
        hotel_data_1 = {'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','ota_reference':'https://www.abchotel.com','website':'','review':0}
        my_hotel_1 = tc_helper.create_hotelOTA(hotel_data_1)
        self.hotel_1 = my_hotel_1
        
        # Create ClientHotel
        client_hotel_data = {'state':0,'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','website':'https://www.abchotel.com','review':5,'pms_sync':0,'pms':None,'notes':'Test Notes','client':my_admin,'all_room_pricing':False,'predefined_rate':False,'number_of_rooms':5,'subscription_id':'JJhSoghRbkXr7IfWn','using_override_bill':False,'monthly_bill':None,'expiry_date':None,'next_charge':None,'show_free_trial_date_in_expired':True,'hotel_reference':my_hotel_1}
        my_client_hotel = tc_helper.create_ClientHotel(client_hotel_data)
        self.my_client_hotel = my_client_hotel

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'username':'kanhasoft@mail.com','password':'123456','first_name':'kanhasoft','last_name':'kanhasoft'}
        response = self.client.post('/account/client/register/',data, format='json')
        self.client_id = response.data.get('id')

        # Client Hotel Token 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post('/account/auth/hotel/'+str(self.my_client_hotel.id)+'/', format='json')
        self.hoteltoken = json.loads((response.content)).get('token')

    def test_hotel_update_invalid_url(self):
        self.client = APIClient()
        data = {}
        response = self.client.post('/hotel/register', data , format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/register/')

    def test_hotel_update_without_authorization(self):
        self.client = APIClient()
        data = {}
        response = self.client.patch('/hotel/update/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_hotel_update_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        data = {}
        response = self.client.patch('/hotel/update/', data , format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_hotel_update_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        data = {}
        response = self.client.patch('/hotel/update/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)


    def test_hotel_update_with_correct_key_authorization_with_correct_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.hoteltoken)
        data = {'number_of_rooms':"25",'all_room_pricing':1}
        response = self.client.patch('/hotel/update/',data, format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()

# # Test Class for Link Hotel To Client
# # Test Class for this API :- url(r'^link/$', hotel_views.LinkHotelToClient.as_view()),
class LinkHotelToClientTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':datetime.datetime.now()}
        my_admin = tc_helper.create_user(data)
        self.my_admin = my_admin

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')
        self.admin = json.loads((response.content)).get('user')
        
        # Create Hotel 1
        hotel_data_1 = {'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','ota_reference':'https://www.abchotel.com','website':'','review':0}
        my_hotel_1 = tc_helper.create_hotelOTA(hotel_data_1)
        self.hotel_1 = my_hotel_1
        
        # Create ClientHotel
        client_hotel_data = {'state':0,'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','website':'https://www.abchotel.com','review':5,'pms_sync':0,'pms':None,'notes':'Test Notes','client':my_admin,'all_room_pricing':False,'predefined_rate':False,'number_of_rooms':5,'subscription_id':'JJhSoghRbkXr7IfWn','using_override_bill':False,'monthly_bill':None,'expiry_date':None,'next_charge':None,'show_free_trial_date_in_expired':True,'hotel_reference':my_hotel_1}
        my_client_hotel = tc_helper.create_ClientHotel(client_hotel_data)
        self.my_client_hotel = my_client_hotel

        # client register
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'username':'kanhasoft@mail.com','password':'123456','first_name':'kanhasoft','last_name':'kanhasoft'}
        response = self.client.post('/account/client/register/',data, format='json')
        self.client_id = response.data.get('id')

        self.client = APIClient()
        system_region = system_models.Region.objects.create(region='IN')
        self.region = system_region
        system_country=system_models.Country.objects.create(name='IN',abbreviation='in',region=system_region)
        self.country = system_country
        system_Currency = system_models.Currency.objects.create(name='Indian Rupee', abbreviation='INR', symbol='INR')
        self.currency = system_Currency

        # Reseller Access    
        self.reseller, self.responsible_person = tc_helper.setResellerAccess()

    def test_link_hotel_to_client_invalid_url(self):
        self.client = APIClient()
        data = {}
        response = self.client.post('/hotel/link', data , format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/link/')

    def test_link_hotel_to_client_without_authorization(self):
        self.client = APIClient()
        data = {}
        response = self.client.post('/hotel/link/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_link_hotel_to_client_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.token)
        data = {}
        response = self.client.post('/hotel/link/', data , format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_link_hotel_to_client_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        data = {}
        response = self.client.post('/hotel/link/', data , format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_link_hotel_to_client_with_correct_key_authorization_with_wrong_key_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        data = {'cli_ent':self.client_id,'hot_el':'12345','currency':self.currency.id}
        response = self.client.post('/hotel/link/',data, format='json')
        client = json.loads((response.content)).get('client')
        hotel = json.loads((response.content)).get('hotel')
        currency = json.loads((response.content)).get('currency')
        statusflag = True
        if client['message'] == 'client is required':
            statusflag = False
        elif hotel['message'] == "hotel does not exists":
            statusflag = False
        elif currency['message'] == "This field is required.":
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_link_hotel_to_client_with_correct_key_authorization_with_wrong_hotel_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        reference_room_data = {"name": "Double Room", "max_occupancy": '2', "avg_price": '125'}
        data = {'client':self.my_admin.id,'hotel':123,'number_of_rooms':'20','currency':self.currency.id,'reference_room_data':reference_room_data}
        response = self.client.post('/hotel/link/',data, format='json')
        hotel = json.loads((response.content)).get('hotel')
        statusflag = True
        if hotel['message'] == 'hotel does not exists':
            statusflag = False
        self.assertEquals(statusflag, False)  

    def test_link_hotel_to_client_with_correct_key_authorization_with_wrong_user_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        reference_room_data = {"name": "Double Room", "max_occupancy": '2', "avg_price": '125'}
        data = {'client':154,'hotel':self.my_client_hotel.id,'number_of_rooms':'20','currency':self.currency.id,'reference_room_data':reference_room_data}
        response = self.client.post('/hotel/link/',data, format='json')
        user = json.loads((response.content)).get('user')
        statusflag = True
        if user['message'] == 'user does not exists':
            statusflag = False
        self.assertEquals(statusflag, False)          
    

    def test_link_hotel_to_client_with_correct_key_authorization_with_correct_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        my_hotel = hotel_models.HotelOTA.objects.create(lat='71',lng='72',address='ahmedabad',region='xyz',
        postcode='38004',country=self.country,name='abc hotel',ota_reference='https://www.booking.com/hotel/be/moom.en-gb.html',website='www.abc.com',review=15)
        
        reference_room_data = {"name": "Double Room", "max_occupancy": '2', "avg_price": '125'}
        data = {'client':self.client_id,'hotel':my_hotel.id,'review':0,'number_of_rooms':'20','currency':self.currency.id,'reference_room_data':json.dumps(reference_room_data),'reseller':self.reseller.id,'responsible_person':self.responsible_person.id}
        response = self.client.post('/hotel/link/',data, format='json')
        self.assertTrue(status.is_success(response.status_code))
    
    @classmethod
    def tearDownClass(self):    
        tc_helper.remove_all_records_db()

# Test Class for Checkout
# Test Class for this API :- url(r'^payment/checkout/$', hotel_views.Checkout.as_view()),
class PaymentCheckoutTest(unittest.TestCase):
    # before running each test case,setup function will add one user in table
    @classmethod
    def setUpClass(self):
        self.client = APIClient()
        data = {'username':'admin@mail.com','password':'123456','is_active':True,'is_staff':True,'belongs':None,'free_trial_end':(datetime.datetime.now() + datetime.timedelta(days=10))}
        my_admin = tc_helper.create_user(data)

        data = {'email': 'admin@mail.com', 'password': '123456'}
        response = self.client.post('/account/auth/', data, format='json')
        self.token = json.loads((response.content)).get('token')
        self.admin = json.loads((response.content)).get('user')
        
        # Create Hotel 1
        hotel_data_1 = {'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','ota_reference':'https://www.abchotel.com','website':'','review':0}
        my_hotel_1 = tc_helper.create_hotelOTA(hotel_data_1)
        self.hotel_1 = my_hotel_1
        
        # Create ClientHotel
        client_hotel_data = {'state':0,'lat':'50.2821796','lng':'12.232491200000027','address':'Bad Elster, Germany','region':'Saxony','postcode':'8645','name':'Test Case Hotel','website':'https://www.abchotel.com','review':5,'pms_sync':0,'pms':None,'notes':'Test Notes','client':my_admin,'all_room_pricing':False,'predefined_rate':False,'number_of_rooms':5,'subscription_id':'JJhSoghRbkXr7IfWn','using_override_bill':False,'monthly_bill':None,'expiry_date':None,'next_charge':None,'show_free_trial_date_in_expired':True,'hotel_reference':my_hotel_1}
        my_client_hotel = tc_helper.create_ClientHotel(client_hotel_data)
        self.my_client_hotel = my_client_hotel

        # Client Hotel Token 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post('/account/auth/hotel/'+str(self.my_client_hotel.id)+'/', format='json')
        self.hoteltoken = json.loads((response.content)).get('token')

    def test_payment_checkout_invalid_url(self):
        self.client = APIClient()
        response = self.client.post('/hotel/payment/checkout', format='json')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(isinstance(response, HttpResponsePermanentRedirect))
        self.assertEqual(response.get('location'), '/hotel/payment/checkout/')

    def test_payment_checkout_without_authorization(self):
        self.client = APIClient()
        response = self.client.post('/hotel/payment/checkout/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)
    
    def test_payment_checkout_with_wrong_key_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_UTHORIZATION='Token ' + self.hoteltoken)
        response = self.client.post('/hotel/payment/checkout/', format='json')
        detail = json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Authentication credentials were not provided.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_payment_checkout_with_wrong_token_authorization(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token xxx')
        response = self.client.post('/hotel/payment/checkout/', format='json')
        detail=json.loads((response.content)).get('detail')
        statusflag = True
        if detail == 'Invalid token.':
            statusflag = False
        self.assertEquals(statusflag, False)

    def test_payment_checkout_with_correct_key_authorization_with_correct_data(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.hoteltoken)
        response = self.client.post('/hotel/payment/checkout/', format='json')
        self.assertTrue(status.is_success(response.status_code))

    @classmethod
    def tearDownClass(self):
        tc_helper.remove_all_records_db()



