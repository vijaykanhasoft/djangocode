from django.conf.urls import url

from hotel.views import hotel_views, room_view, individual_date_adjustment_view, daily_adjustment_view, \
    monthly_adjustment_view, hotel_data_model_view, skip_pricing_view, perdefined_rate_view, booking_prop_view, \
    competitor_view, inventory_view, pms_view, pro_settings_view, time_to_booking_adjustment_view, \
    reservation_view, price_note_view ,booking_scraper_view, booking_suite_view, predefined_booking_prop_view, smxapi_view, cubilisapi_view
 
from spyne.server.django import DjangoView

urlpatterns = [
    # hotel
    url(r'^list/$', hotel_views.HotelList.as_view()),
    url(r'^last-pricing-update/$', hotel_views.GetLastUpdateAndPricing.as_view()),
    url(r'^client/list/$', hotel_views.ClientHotelList.as_view()),
    url(r'^client/list/export/$', hotel_views.download_client_list),
    url(r'^client/detail/$', hotel_views.ClientHotelDetail.as_view()),
    url(r'^register/$', hotel_views.HotelRegister.as_view()),
    url(r'^update/$', hotel_views.HotelUpdate.as_view()),
    url(r'^pms-sync/update/$', hotel_views.HotelUpdatePmsSync.as_view()),
    url(r'^link/$', hotel_views.LinkHotelToClient.as_view()),
   
]
