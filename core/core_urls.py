from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

app_name= 'core_urls'
urlpatterns = [
    path('',views.home, name="home"),
    path('index',views.index, name="index" ),
    path('detailView/<int:id>/',views.detailView,name="detailView"),
    path("hostel/<int:id>/", views.hostel_detail, name="hostel_detail"),
    path("search/", views.search_pgs, name="search_pgs"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path('help-center/', views.help_center, name='help_center'),
    path('terms-of-service/', views.terms, name='terms'),
    path('privacy-policy/', views.privacy, name='privacy'),
]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)