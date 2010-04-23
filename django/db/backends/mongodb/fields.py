from django.db import models
from django.db.models import Field
from django.db.models.fields import FieldDoesNotExist
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
            
        if getattr(cls, 'mongodb', None) is None:
            # Create the default manager, if needed.
            try:
                cls._meta.get_field('mongodb')
                raise ValueError("Model %s must specify a custom Manager, because it has a field named 'objects'" % cls.__name__)
            except FieldDoesNotExist:
                pass
            setattr(cls, 'mongodb', Manager())

signals.class_prepared.connect(add_mongodb_manager)