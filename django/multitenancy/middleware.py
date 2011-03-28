#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Brainaetic: http://www.thenetplanet.com
#Copyright 2010 - The Net Planet Europe S.R.L.  All Rights Reserved. 

from django.multitenancy.settings import settings, get_tenancy_key

class MultiTenancyMiddleware(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def __init__(self):
        from django.core.exceptions import MiddlewareNotUsed
        from django.conf import settings as djsettings
        if not djsettings.MULTITENANCY:
            raise MiddlewareNotUsed()

    def process_request(self, request):

        from brainaetic.utils.stringutils import patterns
        from django.conf import settings as djsettings
        ignore = patterns(False, *djsettings.REQUEST_IGNORE_PATHS)

        def set_key(key):
            settings.set_key(key)
#            load_session(request)
#            request.session['apikey'] = key
            return True

        if ignore.resolve(request.path[1:]):
            return

        for attr in ['REQUEST', 'META', 'COOKIES']:
            key, key2 = getattr(request, attr).get('HTTP_APIKEY', None), getattr(request, attr).get('apikey', None)
            
            if key or key2:
                set_key(key or key2)
                return

#        def load_session(request):
#            from django.utils.importlib import import_module
#            engine = import_module(djsettings.SESSION_ENGINE)
#            session_key = request.COOKIES.get(djsettings.SESSION_COOKIE_NAME, None)
#            request.session = engine.SessionStore(session_key)
#
#        load_session(request)
#
#        key = request.session.get('apikey', None)
#        if key:
#            set_key(key)
#            print "Set key by session", key
#            return

#        print "Set key default"
        set_key('default')

    def process_response(self, request, response):
        """Set up the apikey"""
        response.set_cookie("apikey", value=get_tenancy_key(), httponly=True)
        return response
