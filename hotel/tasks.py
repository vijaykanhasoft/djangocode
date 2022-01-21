from celery import shared_task
from django.conf import settings
from hotel import models as hotel_models
from hotel.integration import protel_ota_format as ota_format_helper, guestline_ota_format, cubilis_ota_format



@shared_task(queue='guestline')
def guestline_response(reservation_id): 
    guestline_hp = guestline_ota_format.GuestLine()
    p_data = hotel_models.XMLEndpointLog.objects.filter(id=reservation_id)
    if len(p_data) > 0 :
        p_data = p_data.first()
        
        if p_data.request_type == 3 :            
            guestline_hp.hotel_inv_count(p_data)

        elif p_data.request_type == 9 :            
            guestline_hp.hotel_rate_amount(p_data)

@shared_task(queue='cubilis')
def cubilis_response(reservation_id):
    cubilis_hp = cubilis_ota_format.Cubilis()
    p_data = hotel_models.XMLEndpointLog.objects.filter(id=reservation_id)

    if len(p_data) > 0:
        p_data = p_data.first()
        cubilis_hp.REQUEST_TYPE = p_data.request_type

        if p_data.request_type == 3:
            cubilis_hp.hotel_inv_count_notif(p_data)

        elif p_data.request_type == 5:
            cubilis_hp.hotel_avail_notif(p_data)

