# tracking/urls.py

from django.urls import path
from .views import (
    admin_login,
    customer_login,
    customer_signup,
    transport_login,
    admin_dashboard,
    customer_dashboard,
    driver_dashboard,
    logout_view,
    assign_route,
    transport_dashboard,
    complete_route,
    assign_dispatch_to_warehouse,
    assign_warehouse_to_delivery,
    assign_warehouse_to_warehouse,
    index
)

urlpatterns = [
    path('admin/login/', admin_login, name='admin_login'),
    path('customer/login/', customer_login, name='customer_login'),
    path('customer/signup/', customer_signup, name='customer_signup'),
    path('transport/login/', transport_login, name='transport_login'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('driver/dashboard/', driver_dashboard, name='driver_dashboard'),
    path('assign_route/', assign_route, name='assign_route'),
    path('transport/dashboard/', transport_dashboard, name='transport_dashboard'),
    path('index', index, name = 'index'),
    # Updated URL pattern for complete_route
    path('transport/complete_route/<int:route_id>/', complete_route, name='complete_route'),

    path('assign_dispatch_to_warehouse/', assign_dispatch_to_warehouse, name='assign_dispatch_to_warehouse'),
    path('assign_warehouse_to_warehouse/', assign_warehouse_to_warehouse, name='assign_warehouse_to_warehouse'),
    path('assign_warehouse_to_delivery/', assign_warehouse_to_delivery, name='assign_warehouse_to_delivery'),
    path('logout/', logout_view, name='logout'),
]
