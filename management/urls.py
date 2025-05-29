from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('complaint/edit/<str:complaint_id>/', views.edit_complaint, name='edit_complaint'),
    path('complaint/delete/<str:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('login/', LoginView.as_view(template_name='management/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('', views.index, name='index'),
    path('add-car-details/', views.add_car_details, name='add_car_details'),
    path('delete-car-detail/<int:year_range_id>/', views.delete_car_detail, name='delete_car_detail'),
    path('master-settings/', views.master_settings, name='master_settings'),
    path('delete-master-setting/<int:setting_id>/', views.delete_master_setting, name='delete_master_setting'),
    path('add-complaint/', views.add_complaint, name='add_complaint'),
    path('api/models/<int:brand_id>/', views.get_models, name='get_models'),
    path('api/sub_models/<int:model_id>/', views.get_sub_models, name='get_sub_models'),
    path('api/year_ranges/<int:sub_model_id>/', views.get_year_ranges, name='get_year_ranges'),
        

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
