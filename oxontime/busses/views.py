from django.http import HttpResponse
from collections import defaultdict
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from models import *
from datetime import datetime,date
from django.conf import settings

from oxontime.utils.views import BaseView, renderer

class KMLView(BaseView):
    @renderer(format="kml", mimetypes=('application/kml+xml',))
    def render_kml(self, request, context, template_name):
        return render_to_response('serialize.kml',
                                  context, context_instance=RequestContext(request),
                                  mimetype='application/kml+xml')

xsize = 69
ysize = 92
def home(request):
  table = '<table>\n'
  table += "  <tr><td></td>\n"
  for x in range(1,xsize+1):
    table += '    <td class="h">%s</td>\n' % (x)
  table += "  </tr>\n"
  for y in range(1,ysize+1):
    table += "  <tr><td>%s</td>\n" % (y)
    for x in range(1,xsize+1):
      try:
        r = Region.objects.get(x=x,y=y)
        c = r.bus_set.filter(updated=r.last_updated).count()
        c2 = r.bus_set.count()
        table += '    <td class="c%s">%s<br />%s</td>\n' % (c2, c,r.id)
      except Region.DoesNotExist:
        table += '    <td class="empty">&nbsp;</td>\n'
    table += "  </tr>\n"
  table += "</table>\n"
  return render_to_response('home.fbml', {'table': table})

class ListServicesView(BaseView):
    def initial_context(self, request):
        services = sorted(set(b.service for b in Bus.objects.all()))
        return {
            'services': services,
        }

    def handle_GET(self, request, context):
        return self.render(request, context, 'service-list')

def kml(request):
    out = []
    out.append('<?xml version="1.0" encoding="utf-8" standalone="no"?>')
    out.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    out.append('<Document>')
    for region in Region.objects.all():
        buses = region.bus_set.filter(updated=region.last_updated)
        for bus in buses:
            location = bus.location.transform(4326, clone=True)
            l = tuple(bus.location)
            out.append('<Placemark id="%d">' % bus.pk)
            out.append('<Point>')
            out.append('<coordinates>%f,%f</coordinates>' % tuple(bus.location.transform(4326, clone=True)))
            out.append('</Point>')
            out.append('</Placemark>')
    out.append('</Document>')
    out.append('</kml>')
    return HttpResponse(out, mimetype='application/kml+xml')
