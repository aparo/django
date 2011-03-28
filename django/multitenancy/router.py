#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Brainaetic: http://www.thenetplanet.com
#Copyright 2010 - The Net Planet Europe S.R.L.  All Rights Reserved. 

from django.conf import settings

from django.multitenancy.settings import settings as mtsettings

def model_label(model):
    return '%s.%s' % (model._meta.app_label, model._meta.module_name)

class MultiTenancyRouter(object):
    """
    A router to control all database operations on models in the myapp application
    """
    def __init__(self):
        self.managed_default_apps = [app.split('.')[-1] for app in getattr(settings, 'DEFAULT_MANAGED_APPS', [])]
        self.managed_default_models = getattr(settings, 'DEFAULT_MANAGED_MODELS', [])
        self.default_database = settings.DATABASES['default']

    def model_app_is_default_managed(self, model):
        return model._meta.app_label in self.managed_default_apps

    def model_is_managed(self, model):
        return model_label(model) in self.managed_default_models

    def is_managed(self, model):
        return True

    def db_for_read(self, model, **hints):
        """Point all operations on default of "keyed" models to a multitenancy database"""
        if self.model_app_is_default_managed(model) or self.model_is_managed(model):
            return self.default_database
        return mtsettings.key

    db_for_write = db_for_read # same algorithm

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in myapp is involved"""
        return True

    def allow_syncdb(self, db, model):
        """Always allows"""
        return True
