from django.urls import path
from owner import views
from django.conf import settings
from django.conf.urls.static import static

app_name= 'owner_urls'
urlpatterns = [
    path('owner_dashboard',views.owner_dashboard, name="owner_dashboard" ),
    path('manage_properties', views.manage_properties, name="manage_properties"),
    path('select-property-type', views.select_property_type, name="select-property-type"),
    path('add_rooms/<int:pg_id>/', views.add_rooms, name="add_rooms"),
    path('add_pg', views.add_pg_property, name="add_pg"),
    path('add_hostel', views.add_hostels, name="add_hostel"),
    path('room/<int:room_id>/book/', views.book_room, name='book_room'),
    path("hostel/book/<int:hostel_id>/", views.book_hostel, name="book_hostel"),
    path('manage_bookings', views.manage_bookings, name="manage_bookings")
]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)