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
from pygal.style import BlueStyle

import pygal

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
def list_input_data(request, input):
    data = {}
    data['input'] = get_object_or_404(MeterInput, pk = input)
    entries = Entry.objects.filter(input = data['input'])
    data['search'] = []
    if request.GET.get('date-from', None):
        data['date_from'] = request.GET['date-from']
        data['search'].append("date-from=%s" % (data['date_from']))
        entries = entries.filter(time__gte = data['date_from'])
    if request.GET.get('date-till', None):
        data['date_till'] = request.GET['date-till']
        entries = entries.filter(time__lte = data['date_till']) 
        data['search'].append("date-till=%s" %(data['date_till']))
    if request.GET.get('chart', None):
        entries = entries.order_by('time')
        entries = entries.values_list('value', flat = True)
        chart = pygal.Line(fill = True)

        chart.add("%s readings" % (input) , list(entries))
        return chart.render_django_response()
    else:
        entries = entries.order_by('-time')
        data['entries'] = Paginator(entries, 250).page(request.GET.get('page' , 1))
        data['search'] = '&'.join(data['search'])
        return render(request, "meterdata/list_meter_data.html", data )


def list_statistics(request, input):
    data = {}
    data['input'] = get_object_or_404(MeterInput, pk = input)
    data['search'] = []
    data['aggregate_values'] = ('day', 
                            'week',
                            'month',
                            'quarter',
                            'year') 
    if request.GET.get('show', None):
        data['search'].append("show=true")
        if request.GET.get('date-from', None):
            data['date_from'] = request.GET['date-from']
            data['search'].append("date-from=%s" % (data['date_from']))
        if request.GET.get('date-till', None):
            data['date_till'] = request.GET['date-till']
            data['search'].append("date-till=%s" %(data['date_till']))
        if request.GET.get('aggregate-by', None):
            data['aggregate_by'] = request.GET['aggregate-by']
            data['search'].append("aggregate-by=%s" %(data['aggregate_by']))
        dataset = Entry.objects.get_consumption_statistics(input, data['aggregate_by'], data['date_from'], data['date_till'])
        if request.GET.get('chart', None): 
            chart = pygal.Line(fill = True,  
                                title = 'Input %s consumption statistics from %s till %s' % (input, data['date_from'], data['date_till']),
                                legend_at_bottom = True, tooltip_border_radius =  10, y_title = 'consumption', style=BlueStyle)
            chart.x_labels = [value['day'].strftime("%x") for value in dataset]
            chart.add('%s consumption' % (data['aggregate_by']), [value['consumption']  for value in dataset])
            return chart.render_django_response()
        data['entries'] = Paginator(dataset, 250).page(request.GET.get('page', 1))
        data['search'] = '&'.join(data['search'])
    return render(request, "meterdata/list_statistics.html", data)