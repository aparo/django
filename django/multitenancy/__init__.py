from django.db.models.signals import class_prepared

def add_tenant_property(sender, **kwargs):
    def tenant(self):
        return self._state.db
    setattr(sender, 'tenant', property(tenant))
    
class_prepared.connect(add_tenant_property)