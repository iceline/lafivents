from django.core.management.base import BaseCommand, CommandError

from meterdata.models import MeterInput
from meterdata.models import SyncLog
from meterdata.models import SyncFiles
from meterdata.models import Entry

import os  
import hashlib

from django.utils import timezone

from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'synces file input to database'
    def file_needs_parsed(self, input, file_name, fullname):
        if not file_name.endswith('.dat'):
            return False

        sync_file, created = SyncFiles.objects.get_or_create(input = input, filename = file_name)
        hasher = hashlib.md5()
        with open(fullname, 'rb') as handle:
            buffer = handle.read()
            hasher.update(buffer)
        if sync_file.hash == hasher.hexdigest():
            return False 
        sync_file.hash = hasher.hexdigest()
        return sync_file
    def  parse_file(self, file_name, input, log_file):
        row_count = 1
        with open(file_name) as handle:
            previous = 0
            for line in handle.readlines():
                if not line.startswith("#"):
                    data = line.strip().split('\t')
                    day, month, year = data[0].split('.')
                    hour, minute, second = data[1].split(':')
                    dtime = timezone.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                    value = int(data[2])
                    if previous == 0:
                        delta = 0
                    else:   
                        delta =  value - previous 
                    previous = value
                    try:
                        Entry(log = log_file, input = input, time = timezone.make_aware(dtime), value = value, delta_from_previous = delta).save()
                        row_count += 1 
                    except IntegrityError:
            
                        pass # we have this input failed file :< 
        log_file.rowcount = row_count
        log_file.save()
    def handle(self, *args, **kwargs):
        for input in MeterInput.objects.all():
            log = SyncLog(input = input)
            log.save()
            for dirpath, dnames, fnames in os.walk(input.directory):
                for f in fnames:
                    print("%s  - Started %s " % (timezone.now(), f))
                    log_file =  self.file_needs_parsed(input, f, os.path.join(dirpath, f))
                    if log_file:
                        self.parse_file(os.path.join(dirpath, f), input, log_file)
            log.status = 'success'
            log.finished = timezone.datetime.now()
            log.save()