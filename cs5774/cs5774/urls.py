from django.contrib import admin
from django.urls import path, include
import coviDash

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('coviDash.urls', namespace="coviDash")),
]
 