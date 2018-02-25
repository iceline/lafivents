from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView 
from django.core.paginator import Paginator

from .models import MeterInput
from .models import SyncFiles
from .models import SyncLog
from .models import Entry

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required 
from django.shortcuts import get_object_or_404 

class ListMeters(LoginRequiredMixin, ListView):
    model = MeterInput

@staff_member_required
def sync_files(request):
    data = {}
    files = SyncFiles.objects.all().order_by('-first_seen')
    data['sync_files'] = Paginator(files, 100).page(request.GET.get('page', 1))
    data['last_sync'] =  SyncLog.objects.all().order_by('-started')[0]
    return render(request, "meterdata/sync_files.html", data)

@login_required
def list_input_data(request, input ):
    data = {}
    data['input'] = get_object_or_404(MeterInput, pk = input)
    entries = Entry.objects.filter(input = data['input']).order_by('-time')
    data['entries'] = Paginator(entries, 250).page(request.GET.get('page' , 1))
    return render(request, "meterdata/list_meter_data.html", data )

def list_statistics(request):
    pass