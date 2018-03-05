from django.db import models

import os 

class MeterInput(models.Model):
    title = models.CharField(verbose_name = u'meter title', max_length = 255)
    directory = models.CharField(verbose_name = u'output file directory', max_length = 255, unique =True)
    def get_event_count(self):
        return self.entry_set.count()
    def get_last_event(self):
        return self.entry_set.order_by('-time')[0]
    def get_first_event(self):
        return self.entry_set.order_by('time')[0]
    def __unicode__(self):
        return self.title
    class Meta: 
        verbose_name = u'heat meter'
        verbose_name_plural = u'heat meters' 
        ordering = ['-title']
    def __save__(self, *args, **kwargs):
        if not os.path.isdir(self.directory):
            raise ValueError("%s invalid directory specified " % (self.directory))

        super().save(*args, **kwargs)

SYNC_STATUSES = ( 
    ('start', 'sync started'),
    ('success', 'sync successfull'),
)


class SyncLog(models.Model):
    started = models.DateTimeField(u'started', auto_now_add = True)
    finished = models.DateTimeField(u'ended', default = None, blank = True, null = True) 
    input = models.ForeignKey(MeterInput, verbose_name = 'heat meter', on_delete = models.CASCADE)
    status = models.CharField(u'status', max_length = 10, choices = SYNC_STATUSES, default = 'start')
    class Meta:
        verbose_name = 'sync log'
        ordering = ['-started', '-finished']

class SyncFiles(models.Model):
    input = models.ForeignKey(MeterInput, verbose_name = 'sync log', on_delete = models.CASCADE)
    filename = models.CharField(u'file name', max_length = 255)
    hash = models.CharField(u'file hash', max_length = 32, help_text = 'file hash in MD5 format', blank = True, null = True,default = None )
    rowcount = models.PositiveIntegerField(u'row count', default = 0 )
    first_seen = models.DateTimeField('first seen', auto_now_add = True)
    class Meta:
        unique_together = ('input', 'filename', 'hash')

POSSIBLE_AGGREGATE_VALUES = ('day', 
                            'week',
                            'month',
                            'quarter',
                            'year') 



class EntryManager(models.Manager):
    def get_consumption_statistics(self, input, aggregate_by, date_from, date_till):
        if aggregate_by not in POSSIBLE_AGGREGATE_VALUES:
            raise ValueError("Invalid aggregate value %s " % (aggregate_by))
        qset = self.extra({'day' : "date_trunc('%s', time)" % (aggregate_by)})
        qset = qset.filter(time__gte = date_from, time__lte = date_till)
        qset = qset.values('day').annotate(consumption = models.Sum('delta_from_previous'))
        return qset 

class Entry(models.Model):
    log = models.ForeignKey(SyncFiles, verbose_name = 'sync log', on_delete = models.CASCADE)
    input = models.ForeignKey(MeterInput, verbose_name = 'heat meter', on_delete = models.CASCADE)
    time = models.DateTimeField(u'time')
    value = models.PositiveIntegerField('counter value')
    delta_from_previous = models.PositiveIntegerField(u'delta') 
    objects = EntryManager()
    def __unicode__(self):
        return 'heat meter %s reading %s ' % (self.meter, self.time)
    class Meta:
        verbose_name = 'heat meter reading'
        unique_together = ('input', 'time')