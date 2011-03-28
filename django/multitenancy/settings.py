#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Brainaetic: http://www.thenetplanet.com
#Copyright 2010 - The Net Planet Europe S.R.L.  All Rights Reserved. 

from django.conf import settings as djsettings
from django.utils._threading_local import local
from copy import deepcopy

class ThreadSettings(local):
    key = "default"
    initialized = False
    reset_manager = False

    def __init__(self, **kw):
        if self.initialized:
            raise SystemError('__init__ called too many times')
        self.initialized = True
        self.__dict__.update(kw)

    def set_key(self, name):
        """
        Set the multitenancy key
        """
        if name == getattr(self, 'key', None):
            return

        self.key = name or "default"
        self.reset_manager = True

        if name not in djsettings.DATABASES:
            def_conf = deepcopy(djsettings.DATABASES['default'])
            def_conf['NAME'] = name
            djsettings.DATABASES[name] = def_conf
            if "mongodb" in djsettings.DATABASES:
                def_conf = deepcopy(djsettings.DATABASES['mongodb'])
                def_conf['NAME'] = name
                djsettings.DATABASES[name + '_mongodb'] = def_conf
                

settings = ThreadSettings()

def get_tenancy_key():
    return settings.key
    
def get_db_conf():
    return djsettings.DATABASES[settings.key]