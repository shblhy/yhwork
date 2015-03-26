# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
@author:hy 
渲染器，常见渲染/响应动作
'''
import csv,json
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render_to_response
from django.template.loader import select_template,get_template,Context,find_template,get_template_from_string
FLOAT_REPR = lambda x:"%.2f" % x

def base_encode(value):
    if isinstance(value, float):
        value = FLOAT_REPR(value)
    return value

def render_to_csv_response(csv_filename,rows,columns=None):
    if type(rows) == tuple and columns is None:
        rows,columns = rows
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % csv_filename.encode('gbk')
    writer = csv.writer(response)
    #writer.writerow([r['sTitle'].encode('gbk') if isinstance(r['sTitle'], basestring) else r for r in columns])
    writer.writerow([r.encode('gbk') if isinstance(r, basestring) else base_encode(r) for r in columns])
    for row in rows:
        line = []
        for r in row:
            if isinstance(r, basestring):
                line.append(r.encode('gbk'))
            else:
                line.append(base_encode(r))
        writer.writerow(line)
    return response

class HttpJsonResponse(HttpResponse):
    def __init__(self,res):
        super(HttpJsonResponse, self).__init__(json.dumps(res), content_type='application/json; charset=UTF-8')


def render_to_string_tmpl(pretext,aftertext,template_name, dictionary=None, context_instance=None,
                     dirs=None):
    """
    Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    """
    if isinstance(template_name, (list, tuple)):
        t = select_template(template_name, dirs)
    else:
        t = get_template(template_name, dirs)
    e = [pretext]
    e.extend(t.nodelist)
    t.nodelist = e
    t.nodelist.append(aftertext)
    if not context_instance:
        return t.render(Context(dictionary))
    if not dictionary:
        return t.render(context_instance)
    # Add the dictionary to the context stack, ensuring it gets removed again
    # to keep the context_instance in the same state it started in.
    with context_instance.push(dictionary):
        return t.render(context_instance)

def get_template(template_name, dirs=None):
    template, origin = find_template(template_name, dirs)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template
    
def render_to_tmpl_response(tmpl=('',''),*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'content_type': kwargs.pop('content_type', None)}

    return HttpResponse(render_to_string_tmpl(tmpl[0],tmpl[1],*args, **kwargs), **httpresponse_kwargs)