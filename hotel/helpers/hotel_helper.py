import datetime
import time

from django.conf import settings
from django.core.cache import cache

from hotel import models as hotel_models
from hotel.helpers import pms_helper
from hotel.helpers.pms import apaleo as apaleo_helper, mews as mews_helper, booking_factory as booking_factory_helper, \
    siteminder as siteminder_helper, little_hotelier as little_hotelier_helper, impala as impala_helper, \
    clock as clock_helper, checkfront as checkfront_helper, hotel_spider as hotel_spider_helper, beds24 as beds24_helper , \
    booking_suite as booking_suite_helper, cubilis as cubilis_helper, smx as smx_helper , protel as protel_helper, allotz as allotz_helper, channex as channex_helper,seekom as seekom_helper
from hotel.serializers import hotel_serializer, pms_serializer
import os, sys
import requests
from hotel.validators import hotel_validator, pms_validator
from hotel.helpers import pms_helper
from amalgamation import models as amalgamation_models
import json
from datetime import timedelta
import pricing_algorithm.algorithm.util.CompetitorInfo as CI
from pricing_algorithm import tasks as pricing_algorithm_task
from pricing_algorithm.helpers import price_history, price_cache as price_cache_helper
import chargebee

def extra_action_after_link(pms):
    _updated_room_ids = []
    _updated_rate_ids = []
    if pms.provider == pms_helper.APALEO:
        apaleo_hp = apaleo_helper.Apaleo(pms)
        apaleo_hp.hash_auth_token()
        apaleo_hp.auth()
        apaleo_hp.get_rooms()
        apaleo_hp.get_rates()

        _updated_room_ids = apaleo_hp.updated_room_ids
        _updated_rate_ids = apaleo_hp.updated_rate_ids

    elif pms.provider == pms_helper.MEWS:
        mews_hp = mews_helper.Mews(pms)
        mews_hp.get_rooms()
        mews_hp.get_rates()
        mews_hp.get_service_acomodation()

        _updated_room_ids = mews_hp.updated_room_ids
        _updated_rate_ids = mews_hp.updated_rate_ids

    elif pms.provider == pms_helper.BOOKING_FACTORY or pms.provider == pms_helper.COVER or pms.provider == pms_helper.ALL_IN_ONE:
        booking_factory_hp = booking_factory_helper.BookingFactory(pms)
        booking_factory_hp.get_rooms()
        booking_factory_hp.get_rates()

        _updated_room_ids = booking_factory_hp.updated_room_ids
        _updated_rate_ids = booking_factory_hp.updated_rate_ids

    elif pms.provider == pms_helper.SITEMINDER:
        siteminder_hp = siteminder_helper.SiteMinder(pms)
        siteminder_hp.get_rooms()

        _updated_room_ids = siteminder_hp.updated_room_ids
        _updated_rate_ids = siteminder_hp.updated_rate_ids

    elif pms.provider == pms_helper.LITTLE_HOTELIER:
        little_hotellier_hp = little_hotelier_helper.LittleHotelier(pms)
        little_hotellier_hp.get_rooms()

        _updated_room_ids = little_hotellier_hp.updated_room_ids
        _updated_rate_ids = little_hotellier_hp.updated_rate_ids

    elif pms.provider == pms_helper.IMPALA:
        impala_hp = impala_helper.Impala(pms)
        impala_hp.get_rooms()
        impala_hp.get_rates()

        _updated_room_ids = impala_hp.updated_room_ids
        _updated_rate_ids = impala_hp.updated_rate_ids

    elif pms.provider == pms_helper.CLOCK_SYSTEM:
        clock_hp = clock_helper.Clock(pms)
        clock_hp.get_rooms()
        clock_hp.get_rates()

        _updated_room_ids = clock_hp.updated_room_ids
        _updated_rate_ids = clock_hp.updated_rate_ids

    elif pms.provider == pms_helper.CHECKFRONT:
        checkfront_hp = checkfront_helper.CheckFront(pms)
        checkfront_hp.get_rooms()

        _updated_room_ids = checkfront_hp.updated_room_ids
        _updated_rate_ids = checkfront_hp.updated_rate_ids

    elif pms.provider == pms_helper.HOTEL_SPIDER or pms.provider == pms_helper.GLOBERES or pms.provider == pms_helper.BOCCO:
        hotel_spider_hp = hotel_spider_helper.Spider(pms)
        hotel_spider_hp.get_rooms()
        #hotel_spider_hp.get_rates()

        _updated_room_ids = hotel_spider_hp.updated_room_ids
        _updated_rate_ids = hotel_spider_hp.updated_rate_ids
    elif pms.provider == pms_helper.BEDS24 or pms.provider == pms_helper.BOOKING_AUTOMATION:
        beds24_hp = beds24_helper.Beds24(pms)
        beds24_hp.get_rooms()
        beds24_hp.get_rates()

        _updated_room_ids = beds24_hp.updated_room_ids
        _updated_rate_ids = beds24_hp.updated_rate_ids

    elif pms.provider == pms_helper.BOOKING_SUITE:
        booking_suite_hp = booking_suite_helper.BookingSuite(pms)
        booking_suite_hp.get_rooms()
        booking_suite_hp.get_rates()

        _updated_room_ids = booking_suite_hp.updated_room_ids
        _updated_rate_ids = booking_suite_hp.updated_rate_ids

    elif pms.provider == pms_helper.CUBILIS:
        cubilis_hp = cubilis_helper.Cubilis(pms)
        cubilis_hp.get_rooms_and_rates()

        _updated_room_ids = cubilis_hp.updated_room_ids
        _updated_rate_ids = list(set(cubilis_hp.updated_rate_ids))

    elif pms.provider == pms_helper.SMX:
        smx_hp = smx_helper.SMX(pms, pms.extra)
        smx_hp.get_rooms()
        smx_hp.get_rates()

        _updated_room_ids = smx_hp.updated_room_ids
        _updated_rate_ids = list(set(smx_hp.updated_rate_ids))

    elif pms.provider == pms_helper.ALLOTZ:
        allotz_hp = allotz_helper.Allotz(pms)
        allotz_hp.get_rooms_and_rates()

        _updated_room_ids = allotz_hp.updated_room_ids
        _updated_rate_ids = allotz_hp.updated_rate_ids

    elif pms.provider == pms_helper.CHANNEX:
        channex_hp = channex_helper.Channex(pms)
        channex_hp.get_rooms()
        channex_hp.get_rates()

        _updated_room_ids = channex_hp.updated_room_ids
        _updated_rate_ids = channex_hp.updated_rate_ids

    elif pms.provider == pms_helper.SEEKOM:
        
        seekom_hp=seekom_helper.Seekom(pms)
        seekom_hp.get_rooms_and_rates()
        _updated_room_ids = seekom_hp.updated_room_ids
        _updated_rate_ids = seekom_hp.updated_rate_ids
        


    return _updated_room_ids,_updated_rate_ids


def get_pms_reservation(hotel, start_date, end_date):
    reservation = None
    pms = pms_validator.hotel_pms(hotel)
    if pms.provider == pms_helper.BOOKING_SUITE:        
        booking_suit_hp = booking_suite_helper.BookingSuite(pms)
        booking_suit_hp.get_reservation(start_date, end_date)
        reservation = booking_suit_hp.pms_reservation
    
    elif pms.provider == pms_helper.CUBILIS:
        cubilis_hp = cubilis_helper.Cubilis(pms)
        cubilis_hp.get_reservation(start_date, end_date)
        reservation = cubilis_hp.pms_reservation

    elif pms.provider == pms_helper.BEDS24 or pms.provider == pms_helper.BOOKING_AUTOMATION:
        beds24_hp = beds24_helper.Beds24(pms)
        beds24_hp.get_reservation(start_date, end_date)
        reservation = beds24_hp.pms_reservation
        
    elif pms.provider == pms_helper.MEWS:
        mews_hp = mews_helper.Mews(pms)
        mews_hp.get_reservation(start_date, end_date)
        reservation = mews_hp.pms_reservation

    elif pms.provider == pms_helper.SEEKOM:
    
        seekom_hp=seekom_helper.Seekom(pms)
        seekom_hp.get_reservation(start_date, end_date)
        reservation=seekom_hp.pms_reservation

    return reservation

def _get_save_pms_reservation(hotel, start_date, end_date):    
    reservation = get_pms_reservation(hotel, start_date, end_date)
    if reservation:
        status = _write_pms_reservation_to_db(reservation)

        return status
    return False

def _write_pms_reservation_to_db(reservation):
    try:        
        for each_reservation in reservation:
            pms_reservation, created = hotel_models.PmsReservation.objects.get_or_create(reservation_id=each_reservation.get('reservation_id'), pms_id=each_reservation.get('pms').id)
            pms_reservation.date_of_reservation = each_reservation.get('reservation_date')
            pms_reservation.guest_count = each_reservation.get('total_guests')
            pms_reservation.roomtype = each_reservation.get('room_type_id')
            pms_reservation.start_date_of_stay = each_reservation.get('check_in_date')
            pms_reservation.end_date_of_stay = each_reservation.get('check_out_date')
            pms_reservation.price = each_reservation.get('price')
            pms_reservation.currency = each_reservation.get('currency')            
            pms_reservation.save()
        return True
    except Exception as e:
        raise e

def _get_save_booking_suite_reservation(hotel, start_date, end_date):    
    booking_suit_hp = booking_suite_helper.BookingSuiteReservation(hotel)
    booking_suit_hp.get_reservation(start_date, end_date)
    reservations = booking_suit_hp.booking_suite_reservation    
    if len(reservations) > 0:
        status = _write_booking_suite_reservation_to_db(reservations)

        return status, reservations
    else:
        return False, booking_suit_hp.error_message

def _write_booking_suite_reservation_to_db(reservations):
    try:        
        for each_reservation in reservations:
            BS_reservation, created = hotel_models.BookingSuiteReservation.objects.get_or_create(reservation_id=each_reservation.get("reservation_id"))
            BS_reservation.date_of_reservation = each_reservation.get("reservation_date")
            BS_reservation.guest_count = each_reservation.get("total_guests")
            BS_reservation.roomtype = each_reservation.get("room_type_id")
            BS_reservation.start_date_of_stay = each_reservation.get("check_in_date")
            BS_reservation.end_date_of_stay = each_reservation.get("check_out_date")
            BS_reservation.price = each_reservation.get("price")
            BS_reservation.currency = each_reservation.get("currency")            
            BS_reservation.save()
        return True
    except Exception as e:
        raise e



def reset_all_room_and_rates(hotel):
    rooms = hotel_models.ClientRoomInformation.objects.filter(hotel=hotel)
    for room in rooms:
        room.pms_room = None
        room.pms_rate = None
        room.pms_price_applicable_occupancy = None
        room.save()


def on_demand_scrape(competitor,hotel_auth):
    json_hotels_url  = json.dumps([competitor.hotel.ota_reference,])
    json_competitor_ids = json.dumps([competitor.hotel.id,])
    on_demand_data = amalgamation_models.OnDemandScrape.objects.create(
        hotel_url_list = json_hotels_url,
        competitor_list = json_competitor_ids,
        hotel_request = hotel_auth,
    )
    requests.post(settings.SCRAPE_URL + "demand/", data=
    {
        'key': settings.SCRAPE_SECRET_KEY,
        'program': on_demand_data.id,
        'hotel_name': hotel_auth.name,
    })

def on_demand_scrape_multiple_competitor(competitor_hotel_list,client_hotel_id):
    hotel_url_list = hotel_models.HotelOTA.objects.filter(id__in = competitor_hotel_list).values_list("ota_reference", flat=True)
    json_hotels_url  = json.dumps([','.join(hotel_url_list)])
    json_competitor_ids = json.dumps(competitor_hotel_list)
    
    hotel_details = hotel_models.ClientHotel.objects.get(id = client_hotel_id) 
    
    on_demand_data = amalgamation_models.OnDemandScrape.objects.create(
        hotel_url_list = json_hotels_url,
        competitor_list = json_competitor_ids,
        hotel_request_id = client_hotel_id
    )

    requests.post(settings.SCRAPE_URL + "demand/", data=
    {
        'key': settings.SCRAPE_SECRET_KEY,
        'program': on_demand_data.id,
        'hotel_name': hotel_details.name,
    })


def upload_price_to_pms(hotel_id,start_date,end_date,specific_date,room_id=None):
    _hotel = hotel_validator.client_hotel_exists(hotel_id)
    _hotel_property_hp = HotelPropertyHelper(_hotel)
    # print("self.rooms",_hotel_property_hp.rooms)
    # _cached_price = cache.get("pricing-" + str(hotel_id))
    price_cache_hp = price_cache_helper.PriceCache(_hotel)
    _cached_price = price_cache_hp.price_cache
    #print("_cached_price",_cached_price)
    
    _skip_pricing_dates = []
    for _skip_price_record in hotel_models.SkipPricing.objects.filter(hotel = _hotel,date__gte=datetime.date.today()):
        _skip_pricing_dates.append(_skip_price_record)

    _upload_price_result = {}
    
    if specific_date is not None:
        _dates = [specific_date,]
    else:
        _start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        _end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() + datetime.timedelta(days=1)
        _dates = [str(datetime.date.fromordinal(i)) for i in range(_start_date.toordinal(), _end_date.toordinal())]
    
    for _skip_date in _skip_pricing_dates:
        try:
            if _skip_date.fixed_price is None:
                _dates.remove(str(_skip_date.date))
        except:
            pass

    _pms = _hotel.pms
    if specific_date is not None and room_id is not None:
        if _pms.provider == pms_helper.BEDS24 or _pms.provider == pms_helper.BOOKING_AUTOMATION:
            _rooms = _hotel_property_hp.rooms.exclude(pms_room=None).filter(id=room_id)
        else:
            _rooms = _hotel_property_hp.rooms.exclude(pms_rate=None).filter(id=room_id)
    elif _hotel.all_room_pricing:
        if _pms.provider == pms_helper.BEDS24 or _pms.provider == pms_helper.BOOKING_AUTOMATION:
            _rooms = _hotel_property_hp.rooms.exclude(pms_room=None)
        else:
            _rooms = _hotel_property_hp.rooms.exclude(pms_rate=None)
    else:
        if _pms.provider == pms_helper.BEDS24 or _pms.provider == pms_helper.BOOKING_AUTOMATION:
            _rooms = _hotel_property_hp.rooms.exclude(pms_room=None).filter(is_reference_room=True)
        else:
            _rooms = _hotel_property_hp.rooms.exclude(pms_rate=None).filter(is_reference_room=True)


    if _pms.provider == pms_helper.APALEO:
        apaleo_hp = apaleo_helper.Apaleo(_pms)
        apaleo_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = apaleo_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] =_push_price_result
    elif _pms.provider == pms_helper.MEWS:
        mews_hp =  mews_helper.Mews(_pms)
        mews_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = mews_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result
    elif _pms.provider == pms_helper.BEDS24 or _pms.provider == pms_helper.BOOKING_AUTOMATION:
        beds24_hp = beds24_helper.Beds24(_pms)
        beds24_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            prepare_room_price_data = beds24_hp.prepare_room_price_data(room,_cached_price,_dates)
            _push_price_result = beds24_hp.upload_prices(prepare_room_price_data)
            _upload_price_result[str(room.id)] = _push_price_result


    elif (_pms.provider == pms_helper.BOOKING_FACTORY) or (_pms.provider == pms_helper.COVER) or (_pms.provider == pms_helper.ALL_IN_ONE):
        booking_factory_hp = booking_factory_helper.BookingFactory(_pms)
        booking_factory_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = booking_factory_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result



    elif _pms.provider == pms_helper.CLOCK_SYSTEM:
        clock_hp = clock_helper.Clock(_pms)
        clock_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = clock_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result
    elif (_pms.provider == pms_helper.HOTEL_SPIDER) or (_pms.provider == pms_helper.GLOBERES) or (_pms.provider == pms_helper.BOCCO):
        hotel_spider_hp = hotel_spider_helper.Spider(_pms)
        hotel_spider_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = hotel_spider_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result
    
    elif _pms.provider == pms_helper.LITTLE_HOTELIER:
        little_hotellier_hp = little_hotelier_helper.LittleHotelier(_pms)

        _upload_price_result = little_hotellier_hp.upload_prices(start_date, end_date, _rooms, _cached_price, _dates, specific_date)
        
    elif _pms.provider == pms_helper.SITEMINDER:
        siteminder_hp = siteminder_helper.SiteMinder(_pms)

        _upload_price_result = siteminder_hp.upload_prices(start_date, end_date, _rooms, _cached_price, _dates, specific_date)
        
    elif _pms.provider == pms_helper.PROTEL:
        protel_hp = protel_helper.Protel(_pms)
        protel_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        # for room in _rooms:
        _push_price_result = protel_hp.upload_prices(_cached_price,_dates,_rooms) 
        for room in _rooms:
            _upload_price_result[str(room.id)] = _push_price_result

    elif _pms.provider == pms_helper.SMX:
        if _pms.extra == "littlehotelier":            
            little_hotellier_hp = little_hotelier_helper.LittleHotelier(_pms)
            for room in _rooms:
                _push_price_result = little_hotellier_hp.upload_prices(start_date, end_date, room, _cached_price,_dates, specific_date)
                _upload_price_result[str(room.id)] = _push_price_result

        elif _pms.extra == "channelmanager":            
            siteminder_hp = siteminder_helper.SiteMinder(_pms)
            for room in _rooms:
                _push_price_result = siteminder_hp.upload_prices(start_date,end_date,room,_cached_price,_dates,specific_date)
                _upload_price_result[str(room.id)] = _push_price_result

    elif _pms.provider == pms_helper.CUBILIS:
        cubilis_hp = cubilis_helper.Cubilis(_pms)
        cubilis_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)

        for room in _rooms:
            _push_price_result = cubilis_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result

    elif _pms.provider == pms_helper.ALLOTZ:
        allotz_hp = allotz_helper.Allotz(_pms)
        allotz_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)

        for room in _rooms:
            _push_price_result = allotz_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result            
 
    elif _pms.provider == pms_helper.CHANNEX:
        channex_hp = channex_helper.Channex(_pms)
        channex_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)

        _upload_price_result = channex_hp.upload_prices(_cached_price,_dates,_rooms)

    elif _pms.provider == pms_helper.SEEKOM:
        seekom_hp = seekom_helper.Seekom(_pms)
        seekom_hp.pms_prices_dict = pms_price_to_dict(_hotel,start_date,end_date,specific_date)
        for room in _rooms:
            _push_price_result = seekom_hp.upload_prices(_cached_price,_dates,room)
            _upload_price_result[str(room.id)] = _push_price_result

    update_cache_original_price(hotel_id,_upload_price_result,_cached_price)

    if specific_date is None and len(_dates) > 1 and _pms.provider != pms_helper.PROTEL:
        pricing_algorithm_task.update_last_upload_pms.delay(hotel_id,_upload_price_result)
    
    return _upload_price_result 
 
def pms_price_to_dict(hotel,start_date,end_date,specific_date):
    _pms_prices_dict = {}
    if specific_date is not None:
        _pms_prices = hotel_models.PmsPrice.objects.filter(date=specific_date, room__hotel=hotel)
    else:
        _pms_prices = hotel_models.PmsPrice.objects.filter(date__gte=start_date,date__lte=end_date, room__hotel=hotel)
    for _price in _pms_prices:
        _str_date = str(_price.date)
        _str_room_id = str(_price.room.id)
        if _str_date not in _pms_prices_dict:
            _pms_prices_dict[_str_date] = {}
        _pms_prices_dict[_str_date][_str_room_id] = _price
    return _pms_prices_dict

def update_cache_original_price(hotel_id,_upload_price_result,updated_prices):
    # _cached_price = cache.get("pricing-" + str(hotel_id))
    _hotel = hotel_models.ClientHotel.objects.get(id=hotel_id)
    price_cache_hp = price_cache_helper.PriceCache(_hotel)
    _cached_price = price_cache_hp.price_cache

    current_time = datetime.datetime.now()
    # str_current_time = str(current_time)
    for room_id in _upload_price_result:
        if _upload_price_result.get(room_id).get("success"):
            for _str_date in _cached_price:
                try:
                    if updated_prices.get(_str_date,{}).get(room_id) is not None:
                        _cached_price[_str_date][room_id] = updated_prices[_str_date][room_id]
                except:
                    pass    
    # _cached_price["last_update"] = str_current_time
    # _cached_price["last_update_result"] = json.dumps(_upload_price_result)
    # _cached_price["update_status"] = _get_upload_price_result(_upload_price_result)

    # cache.set("pricing-" + str(hotel_id), _cached_price)
    price_cache_hp.write_price_cache(_cached_price)

def _get_upload_price_result(results):
    status_flag = False
    false_counter = 0

    if len(results) > 0:
        for res in results:
            if "success" in results[res]:
                if results[res]['success'] == False:
                    false_counter += 1
            else:
                false_counter += 1

        if false_counter == 0:
            status_flag = True
    return status_flag

def list_to_chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def interval_dates(start_date,end_date,days_interval):
    _start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    _end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    days_diff = (_end_date-_start_date).days
    current_days = 0
    date_list = []
    while days_diff > current_days :
        start_date = _start_date + timedelta(days=current_days)
        end_date = _start_date + timedelta(days=current_days + days_interval)
        if end_date > _end_date :
            end_date = _end_date
        current_days += (days_interval + 1)
        date_list.append({'start_date':start_date,'end_date':end_date})
    
    return date_list
        
def on_demand_multiple_scrape(competitor_urls,competitor_ids,hotel_auth):
    json_hotels_url  = json.dumps(competitor_urls)
    json_competitor_ids = json.dumps(competitor_ids)
    on_demand_data = amalgamation_models.OnDemandScrape.objects.create(
        hotel_url_list = json_hotels_url,
        competitor_list = json_competitor_ids,
        hotel_request = hotel_auth,
    )
    requests.post(settings.SCRAPE_URL + "demand/", data=
    {
        'key': settings.SCRAPE_SECRET_KEY,
        'program': on_demand_data.id,
        'hotel_name': hotel_auth.name,
    })

def remove_old_pms_room_rate(room_ids,rate_ids,pms):
    pms_rooms = hotel_models.PmsRoom.objects.filter(pms = pms).exclude(id__in = room_ids)
    pms_rates = hotel_models.PmsRate.objects.filter(pms=pms).exclude(id__in = rate_ids)

    pms_rooms.delete()
    pms_rates.delete()

def extract_pms_map_dependent_rate(room,mapped_rooms,mapped_rates):
    str_room_id = str(room.id)
    pms_room_code = room.pms_room.room_id
    _selected_rate = None
    if str_room_id in mapped_rooms:
        _key_name = mapped_rooms.get(str_room_id)
        _selected_rate = mapped_rates.get(pms_room_code, {}).get(_key_name, None)
    return _selected_rate

def extract_pms_map_independent_rate(room,mapped_rooms,mapped_rates):
    str_room_id = str(room.id)
    _key_name = mapped_rooms.get(str_room_id)
    _selected_rate = mapped_rates.get(_key_name, None)
    return _selected_rate

def auto_map_rate_after_pms_link(pms,room_ids,mapped_rooms,mapped_rates):
    hotel = pms.hotel
    rooms = hotel_models.ClientRoomInformation.objects.filter(id__in = room_ids)

    _extract_pms_map_rate_method = extract_pms_map_dependent_rate
    if hotel.pms_is_independent_rate:
        _extract_pms_map_rate_method = extract_pms_map_independent_rate

    for room in rooms:
            _selected_rate =_extract_pms_map_rate_method(room,mapped_rooms,mapped_rates)
            if _selected_rate is not None:
                room.pms_rate_id = _selected_rate.get("id")
                room.save()



def auto_create_map_rooms_after_pms_link(pms):
    hotel = pms.hotel

    linked_pms_rooms = list(hotel_models.ClientRoomInformation.objects.filter(hotel = hotel).exclude(pms_room = None).values_list("pms_room__id",flat=True))

    pms_room_list = hotel_models.PmsRoom.objects.filter(pms=pms).exclude(id__in = linked_pms_rooms)

    _existing_rooms = hotel_models.ClientRoomInformation.objects.filter(hotel = hotel)

    _existing_room_dict = {}
    for _room in _existing_rooms:
        _existing_room_dict[_room.name.lower().strip()] = _room

    is_new_room_generated = False

    for pms_room in pms_room_list:
        pms_room_name = pms_room.name.lower().strip()
        if pms_room_name not in _existing_room_dict:
            _new_room = hotel_models.ClientRoomInformation.objects.create(
                hotel = hotel,
                name = pms_room.name,
                max_occupancy = 2,
                avg_price = 100,
                pms_room = pms_room,

            )
            is_new_room_generated = True
            _existing_room_dict[pms_room_name.lower().strip()] = _new_room
        else:
            _room = _existing_room_dict.get(pms_room_name)
            if _room is not None:
                _room.pms_room = pms_room
                _room.save()
                _existing_room_dict[pms_room_name.lower().strip()] = _room

    if is_new_room_generated:
        hotel_hp = HotelHelper(hotel)
        hotel_hp.set_reference_room()
        hotel_hp.set_derived_rooms_from_db()
        hotel_hp._recalculate_derived_room_pricediff()



class HotelHelper():
    hotel = None
    reference_room = None
    monthly_adjustment = []
    daily_adjustment = []
    expected_occupany = []
    hotel_data_model = None
    competitors = []
    booking_props_default_values = [13, 8.8, 11.3, 11.8, 15.7, 14.5, 7.7, 17.2]
    booking_props = None
    derived_rooms = []
    time_to_booking_adjustment = None

    def __init__(self, hotel):
        self.hotel = hotel

    def set_inngenius_folder_path(self):
        if not os.path.exists(self.hotel.inngenius_folder_path):
            os.makedirs(self.hotel.inngenius_folder_path)

    def set_reference_room(self):
        self.reference_room = hotel_models.ClientRoomInformation.objects.get(hotel=self.hotel, is_reference_room=True)

    def set_derived_rooms_from_db(self):
        self.derived_rooms = hotel_models.ClientRoomInformation.objects.filter(hotel = self.hotel,is_reference_room=False)


    def set_reference_room_avg_price(self, avg_price):
        self.reference_room.avg_price = avg_price
        self.reference_room.save()

    def set_new_reference_room(self, room_id):
        room = hotel_models.ClientRoomInformation.objects.get(id=room_id, hotel=self.hotel)
        room.is_reference_room = True
        room.save()
        self.reference_room = room

    def clear_reference_room(self):
        room = hotel_models.ClientRoomInformation.objects.get(hotel=self.hotel, is_reference_room=True)
        room.is_reference_room = False
        room.save()

    def set_monthly_adjustment(self):
        for month in hotel_models.MONTHS:
            monthly_adjustment = hotel_models.MonthlyAdjustment.objects.create(
                month=month[0],
                average_occupancy=0,
                percentage=0,
                average_price=0,
                monthly_average=0,
                hotel=self.hotel
            )
            self.monthly_adjustment.append(monthly_adjustment)

    def set_daily_adjustment(self):
        for day in hotel_models.DAYS:
            daily_adjustment = hotel_models.DailyAdjustment.objects.create(
                day=day[0],
                average_occupancy=0,
                percentage=0,
                average_price=0,
                daily_average=0,
                hotel=self.hotel
            )
            self.daily_adjustment.append(daily_adjustment)

    def set_hotel_data_model(self):
        self.hotel_data_model = hotel_models.HotelDataModel.objects.create(
            hotel=self.hotel,
            elasticity_weekdays=-5.5000,
            elasticity_weekend=-5.5000,
            universal_price_param_1=0.8,
            universal_price_param_2=0.067,
            universal_price_percentage=0.5,
            universal_price_days_to_checking=14,
        )

    def set_expected_occupancy(self):
        for month in hotel_models.MONTHS:
            monthly_expected_occupancy = hotel_models.ExpectedOccupancy.objects.create(
                month=month[0],
                percentage=100,
                hotel=self.hotel
            )
            self.expected_occupany.append(monthly_expected_occupancy)

    def get_nearest_existing_competitors(self):
        active_competitor_ids = hotel_models.Competitor.objects.filter().exclude(competitor = None).exclude(competitor__number_of_price = 0).distinct("competitor__hotel_id").values_list("competitor__hotel_id",flat=True)
        scrape_list_id = hotel_models.CompetitorHotelList.objects.filter(hotel_id__in = active_competitor_ids).values_list("hotel__id")
        hotel_list = hotel_models.HotelOTA.objects.filter(id__in=scrape_list_id).extra(select={
            'distance': " select (6371.1 * 2 * asin(sqrt(power(sin((radians(%s) - radians(cast(lat as decimal))) / 2), 2) + cos(radians(%s) ) * cos( radians(cast(lat as decimal)) ) * power(sin( (radians(%s) - radians( cast(lng as decimal)) ) / 2), 2) ) ))"},
            select_params=(
                str(self.hotel.lat), str(self.hotel.lat),
                str(self.hotel.lng),), ).order_by(
            'distance').exclude(id=self.hotel.id).values_list('id', flat=True)[:10]
        top_10_competitor_hotel = hotel_models.HotelOTA.objects.filter(pk__in=hotel_list).extra(select={
            'distance': " select (6371.1 * 2 * asin(sqrt(power(sin((radians(%s) - radians(cast(lat as decimal))) / 2), 2) + cos(radians(%s) ) * cos( radians(cast(lat as decimal)) ) * power(sin( (radians(%s) - radians( cast(lng as decimal)) ) / 2), 2) ) ))"},
            select_params=(str(self.hotel.lat), str(self.hotel.lat),
                           str(self.hotel.lng),), ).order_by('distance')[:10]
        top_10_competitor_hotel = top_10_competitor_hotel.values_list("id", flat=True)
        return hotel_models.CompetitorHotelList.objects.filter(hotel__id__in=top_10_competitor_hotel)

    def calculate_pricediff(self, competitor):
        try:
            if competitor is not None and competitor.avg_price is not None:
                decrese = competitor.avg_price - self.reference_room.avg_price
                temp_pricediff = (decrese / competitor.avg_price) * 100
                pricediff = temp_pricediff * (-1)
                return pricediff
        except:
            pass
        return None

    def __clean_competitor__(self, default_competitors, index):
        competitor = None
        weight = 0
        pricediff = None
        try:
            competitor = default_competitors[index]
            weight = 20
            pricediff = self.calculate_pricediff(competitor)
        except:
            pass
        return competitor, weight, pricediff

    def set_competitors(self):
        default_competitors = self.get_nearest_existing_competitors()
        for index in range(1, 11):
            comp, weight, pricediff = self.__clean_competitor__(default_competitors, index-1)
            competitor = hotel_models.Competitor.objects.create(
                index=index,
                competitor=comp,
                pricediff=pricediff,
                weight=weight,
                client_hotel=self.hotel,
            )

            self.competitors.append(competitor)

    def set_competitors_from_db(self):
        self.competitors = hotel_models.Competitor.objects.filter(client_hotel=self.hotel).order_by("index")

    def recalculate_competitors_pricediff(self):
        for competitor in self.competitors:
            competitor.pricediff = self.calculate_pricediff(competitor.competitor)
            competitor.save()

    def set_booking_props(self):
        booking_props_default_values = [13, 8.8, 11.3, 11.8, 15.7, 14.5, 7.7, 17.2]
        booking_prop = hotel_models.BookingProp.objects.create(
            three_months_plus=self.booking_props_default_values[7],
            one_half_months_to_three_months=self.booking_props_default_values[6],
            four_weeks_to_six_weeks=self.booking_props_default_values[5],
            two_weeks_to_four_weeks=self.booking_props_default_values[4],
            one_week_to_two_weeks=self.booking_props_default_values[3],
            four_days_to_seven_days=self.booking_props_default_values[2],
            two_days_to_three_days=self.booking_props_default_values[1],
            last_day=self.booking_props_default_values[0],
            hotel=self.hotel,
        )
        self.booking_props = booking_prop

    def set_time_to_booking_adjustment(self):
        time_to_booking_adjustment = hotel_models.TimeToBookingAdjustment.objects.create(
            adj_six_months_plus=0,
            adj_three_to_six_months=0,
            adj_one_half_months_to_three_months=0,
            adj_four_weeks_to_six_weeks=0,
            adj_one_week_to_two_weeks=0,
            adj_four_days_to_seven_days=0,
            adj_two_days_to_three_days=0,
            adj_last_day=0,

            agg_six_months_plus_id=1,
            agg_three_to_six_months_id=1,
            agg_one_half_months_to_three_months_id=1,
            agg_four_weeks_to_six_weeks_id=1,
            agg_one_week_to_two_weeks_id=1,
            agg_four_days_to_seven_days_id=1,
            agg_two_days_to_three_days_id=1,
            agg_last_day_id=1,

            hotel=self.hotel,
        )
        self.time_to_booking_adjustment = time_to_booking_adjustment
    
    def _get_reference_room(self):
        return hotel_models.ClientRoomInformation.objects.get(hotel=self.hotel, is_reference_room=True)

    def _recalculate_derived_room_pricediff(self,is_refroom_changed=True):
        for room in self.derived_rooms:
            pricediff = 0
            try:
                if room.adjustment_to_reference_room_is_locked and is_refroom_changed:
                    pricediff = room.adjustment_to_reference_room
                    if not room.adjustment_to_reference_room_is_absolute:
                        pricediff = (pricediff/100) * self.reference_room.avg_price

                    room.avg_price = self.reference_room.avg_price + pricediff

                else:
                    pricediff = room.avg_price - self.reference_room.avg_price
                    if not room.adjustment_to_reference_room_is_absolute:
                        pricediff = pricediff / self.reference_room.avg_price
                        pricediff = pricediff * 100
                    room.adjustment_to_reference_room = pricediff
            except:
                room.adjustment_to_reference_room = 0
            room.save()
    
    def _get_inventory(self,start_date,end_date):
        return hotel_models.Inventory.objects.filter(hotel=self.hotel,date__gte=start_date,date__lte=end_date)

    def _get_price(self,start_date,end_date):
        return hotel_models.PmsPrice.objects.filter(room__hotel=self.hotel,date__gte=start_date,date__lte=end_date)

    def recalculate_weighted_avg(self):
        _today = datetime.date.today()
        _end_date = _today + datetime.timedelta(days=370)

        weighted_avg_data = hotel_models.DailyWeightedAverage.objects.filter(date__gte = _today)

        weighted_avg_data.delete()

        _str_today = str(_today)
        _str_end_date = str(_end_date)
        try:
            comp = CI.CompetitorInfo(False, HotelID=self.hotel.id, BookingDateFrom=_str_today, BookingDateTo=_str_end_date,
                                     connectionString=settings.POSTGRES_CREDENTIALS,
                                     weighted_average_data={})

            pricing_algorithm_task.save_weighted_average.delay(comp.adjusted_price_str_key, self.hotel.id, _str_today,
                                                               _str_end_date)
        except:
            pass

    def update_last_price(self):
        current_time = datetime.datetime.now()
        self.hotel.last_run_pricing = current_time
        self.hotel.save()

    def update_last_inventory_price_get(self):
        current_time = datetime.datetime.now()
        self.hotel.last_inventory_price_get = current_time
        self.hotel.save()


class ClientHotelHelper():
    original_hotel = None
    client_hotel = None
    number_of_rooms = 0
    currency = None

    def __init__(self, original_hotel, number_of_rooms, currency,client):
        self.original_hotel = original_hotel
        self.number_of_rooms = int(number_of_rooms)
        self.currency = currency
        self.__copy_hotel__(client)

    def __copy_hotel__(self,client):
        dict_original_hotel = hotel_serializer.HotelSerializer(self.original_hotel, many=False,
                                                               exclude_fields=["id", "country", "ota_reference","currency","competitor_data",]).data

        self.client_hotel = hotel_models.ClientHotel.objects.create(
            **dict_original_hotel,
            number_of_rooms=self.number_of_rooms,
            hotel_reference=self.original_hotel,
            country_id=self.original_hotel.country.id,
            currency=self.currency,
            client = client,
        )
 

class HotelPropertyHelper():
    hotel = None
    pms = None
    reference_room = None
    competitors = None
    skip_pricing_dates = []
    prices_data_dict = {}
    # cache_key = None
    derived_rooms = []
    pms_room_options = []
    pms_rate_options = []
    used_pms_room_ids = []
    mapped_room_rate_options = []
    rooms = []
    analytic = None
    price_cache_hp = None

    def __init__(self, hotel):
        self.hotel = hotel
        self.pms = hotel.pms
        self.reference_room = hotel_models.ClientRoomInformation.objects.get(hotel=self.hotel, is_reference_room=True)
        self._get_competitors()
        # self.cache_key = "prices_" + str(self.hotel.id)
        self.price_cache_hp = price_cache_helper.PriceCache(self.hotel)
        self._getprices_data_cache()
        self.rooms = hotel_models.ClientRoomInformation.objects.filter(hotel = self.hotel)
        self._get_skip_pricing()
        self._get_derived_rooms()
        self._set_analytic_from_db()
        if self.hotel.is_pms_linked:
            self._get_available_pms_room_options()
            self._get_available_pms_rate_options()
            if not self.hotel.pms_is_independent_rate:
                self._map_pms_room_rate()


    def _set_analytic_from_db(self):
        self.analytic,created= hotel_models.Analytic.objects.get_or_create(hotel = self.hotel)

    def _map_pms_room_rate(self):
        self.mapped_room_rate_options = []
        for pms_room in self.pms_room_options:
            mapped_room_rate_data = {}
            pms_room_rates = hotel_models.PmsRate.objects.filter(pms_room=pms_room.room_id, pms=self.hotel.pms)
            serialized_pms_rooms = pms_serializer.PmsRoomSerializer(pms_room, many=False,).data
            serialized_pms_rates = pms_serializer.PmsRateSerializer(pms_room_rates, many=True,
                                                                    exclude_fields=["description", "checkin",
                                                                                   "checkout"]).data
            serialized_pms_rooms["rates"] = serialized_pms_rates

            self.mapped_room_rate_options.append(serialized_pms_rooms)

    def _get_available_pms_room_options(self):
        # self.used_pms_room_ids = hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(
        #     pms_room=None).values_list("pms_room__id")
        self.pms_room_options = hotel_models.PmsRoom.objects.filter(pms=self.hotel.pms).exclude(
            id__in=self.used_pms_room_ids)

    def _get_available_pms_rate_options(self):
        if self.hotel.pms_is_independent_rate:
            used_pms_rate_ids = []
            # used_pms_rate_ids = hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(
            #     pms_rate=None).values_list("pms_rate__id")
            self.pms_rate_options = hotel_models.PmsRate.objects.filter(pms=self.hotel.pms).exclude(
                id__in=used_pms_rate_ids)

    def _get_derived_rooms(self):
        self.derived_rooms = hotel_models.ClientRoomInformation.objects.filter(is_reference_room=False, hotel = self.hotel)

    def _getprices_data_cache(self):
        # self.prices_data_dict = cache.get("pricing-"+str(self.hotel.id))
        self.prices_data_dict =  self.price_cache_hp.price_cache

    def set_price_cache(self, data):
        # cache.set("pricing-"+str(self.hotel.id), data)
        self.price_cache_hp.write_price_cache(data)
        self.prices_data_dict = data

    def _get_competitors(self):
        self.competitors = hotel_models.Competitor.objects.filter(client_hotel=self.hotel)

    def _get_skip_pricing(self):
        self.skip_pricing_dates = hotel_models.SkipPricing.objects.filter(hotel=self.hotel)

    @property
    def rooms_with_linked_pms_rate(self):
        if self.pms.provider == pms_helper.CHECKFRONT:
            return hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(pms_room=None)
        else:
            return hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(pms_rate=None)

    @property
    def rooms_with_linked_pms_room(self):
        return hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(pms_room=None)
        
    @property
    def pms_room_list_id(self):
        return hotel_models.ClientRoomInformation.objects.filter(hotel=self.hotel).exclude(pms_room=None).values_list(
            "pms_room__room_id", flat=True).distinct("pms_room__room_id")

class HotelCompetitorHelper():

    hotel = None
    
    def __init__(self, hotel):
        self.hotel = hotel
        self.competitor = hotel_models.CompetitorHotelList.objects.get(hotel=self.hotel)

    def _get_competitor_details(self):
        return hotel_models.CompetitorHotelList.objects.filter(hotel=self.hotel)

    def _get_competitors_by_client(self):
        return hotel_models.Competitor.objects.filter(competitor__hotel=self.hotel)
    
    def set_hotel_avg_price(self,avg_price):
        self.competitor.avg_price_roomtypes = avg_price
        self.competitor.save()

    def _get_hotel_avg_price(self):
        return self.competitor.avg_price_roomtypes
