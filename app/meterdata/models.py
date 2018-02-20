from django.db import models

import os 

class MeterInput(models.Model):
    title = models.CharField(verbose_name = u'meter title', max_length = 255)
    directory = models.CharField(verbose_name = u'output file directory', max_length = 255)
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