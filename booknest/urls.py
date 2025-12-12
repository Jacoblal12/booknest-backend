"""
URL configuration for booknest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from accounts.views import register_user
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views import AnnouncementViewSet, BookRequestViewSet, BookViewSet, FeedbackViewSet, ReportViewSet, TransactionViewSet, WishlistViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import ProfileViewSet

# Create router FIRST
router = routers.DefaultRouter()

# Register API routes
router.register(r'books', BookViewSet, basename='books')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'transactions', TransactionViewSet, basename="transactions")
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(r'bookrequests', BookRequestViewSet, basename='bookrequests')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # AUTH
    path("api/auth/register/", register_user, name="register"),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

