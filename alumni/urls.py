from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='home'),
    path('graduates', views.graduation_view, name='graduates'),
    path('graduate/<int:graduate_id>/', views.graduate_detail, name='graduate_detail'),
    path('annual-report/', views.annual_report, name='annual_report'),
    path('contact/', views.contact_view, name='contact'),
    path('graduate-search-ajax/', views.graduate_search_ajax, name='graduate_search_ajax'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]