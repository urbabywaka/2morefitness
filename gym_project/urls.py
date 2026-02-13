"""
URL Configuration for 2moreFitness
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ ITO LANG ANG ADMIN URL
    path('', include('apps.core.urls')),
    path('members/', include('apps.members.urls')),
    path('trainers/', include('apps.trainers.urls')),
    path('classes/', include('apps.classes.urls')),
    path('attendance/', include('apps.attendance.urls')),
]

# Serve static + media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

# Customize admin
admin.site.site_header = '2moreFitness Administration'
admin.site.site_title = '2moreFitness Admin'
admin.site.index_title = 'Gym Management System'