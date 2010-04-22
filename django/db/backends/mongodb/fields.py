from django.db import models
from django.db.models import Field
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from pymongo.objectid import ObjectId
from django.db.models import signals
from django.db.models.fields import AutoField as DJAutoField
from .manager import Manager

__all__ = ["EmbeddedModel"]
__doc__ = "Mongodb special fields"

class EmbeddedModel(models.Model):
    _embedded_in =None
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pk = unicode(ObjectId())
        if self._embedded_in  is None:
            raise RuntimeError("Invalid save")
        self._embedded_in.save()

    def serialize(self):
        if self.pk is None:
            self.pk = unicode(ObjectId())
            self.id = self.pk
        result = {'_app':self._meta.app_label, 
            '_model':self._meta.module_name,
            '_id':self.pk}
        for field in self._meta.fields:
            result[field.attname] = getattr(self, field.attname)
        return result

#
# Fix standard models to work with mongodb
#

def autofield_to_python(value):
    if value is None:
        return value
    try:
        return str(value)
    except (TypeError, ValueError):
        raise exceptions.ValidationError(self.error_messages['invalid'])

def autofield_get_prep_value(value):
    if value is None:
        return None
    return ObjectId(value)

def add_mongodb_manager(sender, **kwargs):
    """
    Fix autofield
    """
    cls = sender
    if cls.objects.db =="mongodb":
        if isinstance(cls._meta.pk, DJAutoField):
            pk = cls._meta.pk
            setattr(pk, "to_python", autofield_to_python)
            setattr(pk, "get_prep_value", autofield_get_prep_value)
            cls = sender
        if cls._meta.abstract:
            return
        if hasattr(cls, '_default_manager') and (not isinstance(cls._default_manager, Manager)):
            setattr(cls, 'objects', Manager())
            cls._base_manager = cls.objects
            cls._default_manager = cls.objects
            
        if not getattr(cls, '_default_manager', None):
            # Create the default manager, if needed.
            try:
                cls._meta.get_field('objects')
                raise ValueError("Model %s must specify a custom Manager, because it has a field named 'objects'" % cls.__name__)
            except FieldDoesNotExist:
                pass
            cls.add_to_class('objects', Manager())
            cls._base_manager = cls.objects
        elif not getattr(cls, '_base_manager', None):
            default_mgr = cls._default_manager.__class__
            if (default_mgr is Manager or
                    getattr(default_mgr, "use_for_related_fields", False)):
                cls._base_manager = cls._default_manager
            else:
                # Default manager isn't a plain Manager class, or a suitable
                # replacement, so we walk up the base class hierarchy until we hit
                # something appropriate.
                for base_class in default_mgr.mro()[1:]:
                    if (base_class is Manager or
                            getattr(base_class, "use_for_related_fields", False)):
                        cls.add_to_class('_base_manager', base_class())
                        return
                raise AssertionError("Should never get here. Please report a bug, including your model and model manager setup.")
signals.class_prepared.connect(add_mongodb_manager)