from django.contrib import admin
from django.apps import apps
from .models import *

for mdl in apps.get_models():
    try:
        admin.site.register(mdl)
    except:
        pass

