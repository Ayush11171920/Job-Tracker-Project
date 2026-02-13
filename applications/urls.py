from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-job/', views.add_job, name='add_job'),
    path('edit/<int:id>/', views.edit_job, name='edit_job'),
    path('delete/<int:id>/', views.delete_job, name='delete_job'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout')
]
