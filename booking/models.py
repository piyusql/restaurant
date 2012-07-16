from django.db import models, IntegrityError
from django.db.models import Q
from datetime import datetime, timedelta

DEFAULT_BOOKING_SLOT = 4#hours

# Create your models here.
class Table(models.Model):
    capacity = models.IntegerField()
    is_active = models.BooleanField(default = True)

    class Meta:
        verbose_name = 'Table'
    
    def __unicode__(self):
        return '%(id)s -> %(capacity)s' % self.__dict__

    def is_available(self, start_time, end_time):
        _start_time = datetime.now() if not start_time else start_time
        _end_time = _start_time + timedelta(hours = DEFAULT_BOOKING_SLOT) if not end_time else end_time
        if self.allocations.filter(Q(start_time__lt = _start_time, end_time__gt = _start_time)|\
                Q(start_time__lt = _end_time, end_time__gt = _end_time)):
            return False
        return True

    def delete(self):
        #Table can not be deleted, only de-activated.
        self.is_active = False
        self.save()

class TableAllocation(models.Model):
    table = models.ForeignKey(Table, related_name = 'allocations')
    guest_name = models.CharField(max_length = 25)
    contact_no = models.CharField(max_length = 15)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    booking_time = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        verbose_name = 'TableAllocation'
    
    def __unicode__(self):
        return '%(id)s -> %(contact_no)s' % self.__dict__
   
    def save(self, *args, **kwargs):
        if self.start_time == None:
            self.start_time = datetime.now()
        if self.end_time == None:
            self.end_time = self.start_time + timedelta(hours = DEFAULT_BOOKING_SLOT)
        #if not self.table.is_available(self.start_time, self.end_time):
        #    raise IntegrityError("Table is not free for the given timeslot.")

        super(TableAllocation, self).save(*args, **kwargs)

    def release(self):
        self.end_time = datetime.now()
        self.save()
    
    def delete(self):
        raise IntegrityError("TableAllocation can not be deleted, only released.")
