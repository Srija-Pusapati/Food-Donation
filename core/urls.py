from django.urls import path
from .views import auth_views, dashboard_views, general_views, map_views

urlpatterns = [
    path('', general_views.home, name='home'),
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    
    # Dashboards
    path('donor/', dashboard_views.donor_dashboard, name='donor_dashboard'),
    path('ngo/', dashboard_views.ngo_dashboard, name='ngo_dashboard'),
    path('needy/', dashboard_views.needy_dashboard, name='needy_dashboard'),
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    # Map View
    path('map/', map_views.map_view, name='map_view'),

    # Action endpoints
    path('donor/post/', dashboard_views.post_donation, name='post_donation'),
    path('donor/delete/<int:donation_id>/', dashboard_views.delete_donation, name='delete_donation'),
    path('donor/approve_request/<int:request_id>/', dashboard_views.approve_request, name='approve_request'),
    path('ngo/accept/<int:donation_id>/', dashboard_views.accept_donation, name='accept_donation'),
    path('ngo/update_delivery/<int:delivery_id>/<str:status>/', dashboard_views.update_delivery, name='update_delivery'),
    path('needy/request/<int:donation_id>/', dashboard_views.request_food, name='request_food'),
    path('needy/feedback/<int:donation_id>/', dashboard_views.submit_feedback, name='submit_feedback'),
    path('admin/approve_ngo/<int:user_id>/', dashboard_views.approve_ngo, name='approve_ngo'),
    path('admin/reject_ngo/<int:user_id>/', dashboard_views.reject_ngo, name='reject_ngo'),
]
