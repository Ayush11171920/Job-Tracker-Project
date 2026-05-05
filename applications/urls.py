from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from .views import JobApplicationViewSet

router = DefaultRouter()
router.register(r'jobs', JobApplicationViewSet )

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-job/', views.add_job, name='add_job'),
    path('edit/<int:id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/login/', views.login_api),
    path('api/questions/', views.generate_questions),
    path('ai-questions/', views.ai_questions_page),
    path("signup/", views.signup, name="signup"),
    path('api/', include(router.urls))
    
    

]
