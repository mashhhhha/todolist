from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include(('todolist.core.urls', 'todolist.core'))),
    path('goals/', include(('todolist.goals.urls', 'todolist.goals'))),
    path('oauth/', include('social_django.urls', namespace='social'))
]

if settings.DEBUG:
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls'))
    ]
