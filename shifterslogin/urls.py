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
    path('night-off/', views.night_off, name='night_off'),
    path('revert-off/', views.revert_off, name='revert_off'),
    path('off-details/', views.off_details, name='off_details'),
    path('off-details/', views.off_details, name='off_details'),
    path('modal-check/', views.modal_check, name='modal_check'),
    path('update_endtime/', views.update_endtime, name='update_endtime'),
]
