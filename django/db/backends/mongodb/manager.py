from django.db.models.manager import Manager as DJManager

class Manager(DJManager):
    def find(self, **kwargs):
        print kwargs
        