from django.urls import path
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('start-shift/', views.start_shift, name='start_shift'),
    path('shift-details/', views.shift_details, name='shift_details'),
    path('end-shift/', views.end_shift, name='end_shift'),
    path('start-break/', views.start_break, name='start_break'),
    path('end-break/', views.end_break, name='end_break'),
    path('break-details/', views.break_details, name='break_details'),
]
