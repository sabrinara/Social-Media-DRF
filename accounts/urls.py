from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register(r'user_detail_view', views.UserDetailViewSet, basename='user-detail-view')

urlpatterns = [
    path('register/', views.UserRegistration.as_view(), name='register'),
    path('activate/<uid64>/<token>/', views.activate, name='activate'),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('update/', views.UpdateUserView.as_view(), name='update'),
    # path('user_detail/', views.user_detail, name='user_detail'),
    path('user_detail/', views.UserDetailView.as_view(), name='user_detail'),
]

urlpatterns += router.urls
