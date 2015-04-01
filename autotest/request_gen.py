#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
利用form生产随机数据，封装成为request
'''

import random
import httplib
import urllib
import re
import os
import rstr
import logging
import json
from random_gen import RandVar
from django.forms import fields, models
from django.core.validators import MaxLengthValidator, EmailValidator
from django.core import exceptions, urlresolvers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils.importlib import import_module
from django.template import Context,Template
from django.template.loader import get_template
#from settings import ROOT
from dowant.utils.dj_expand.forms import PageField
from datetime import datetime
log = logging.getLogger('testlog')

def get_random_data(field, mode=RandVar.RIGHT_LIMIT, modelfield=None):
    if modelfield and modelfield.validators:
        validator = modelfield.validators[0]
        if not isinstance(validator, MaxLengthValidator):
            if isinstance(validator, EmailValidator):
                return rstr.letters() + '@' + rstr.lowercase() + '.' + rstr.xeger('^com|cn|net$')
            return RandVar.gen_data(RandVar.REGEX, validator.regex.pattern)
    if hasattr(field, 'gen_random_data'):
        return field.gen_random_data()
    if isinstance(field, PageField):
        return field.default
    if isinstance(field, fields.IntegerField):
        mode = RandVar.INT
        if type(field.min_value) == int and type(field.max_value) == int:
            mode += '_bet_' + str(field.min_value) + '_' + field.max_value
        elif type(field.min_value) == int:
            mode += '_gt_' + str(field.min_value)
        elif type(field.max_value) == int:
            mode += '_lt_' + str(field.max_value)
        return RandVar.gen_data(mode)
    elif isinstance(field, fields.CharField):
        return RandVar.gen_data(RandVar.DEFAULT_STR)
        return RandVar.gen_data(RandVar.ASTR)
    elif isinstance(field, models.ModelChoiceField):
        if field.choices.queryset.count() > 0:
            return field.choices.queryset.all()[random.randint(0, field.choices.queryset.count() - 1)].pk
        else:
            return None
    elif isinstance(field, fields.ChoiceField):
        if len(field.choices) > 0:
            return field.choices[random.randint(0, len(field.choices) - 1)][0]
        else:
            return None
    elif isinstance(field, fields.DateTimeField):
        return RandVar.gen_data(RandVar.TIME_B_1_WEEK)
    elif isinstance(field, fields.Field):
        return RandVar.gen_data(RandVar.DEFAULT_STR)


class RequestSet(object):
    param_pattern = re.compile('.*\?P\<(?P<paramname>.*)\>.*')

    def __init__(self, url_patterns, reqtest, data=None):
        self.url_patterns = url_patterns
        self.host = reqtest.host
        self.cookie = reqtest.cookie
        self.logpath = reqtest.reqlogpath
        self.dopost = reqtest.dopost
        self.data = data
        self.urlconf = reqtest.urlconf.get(self.url_pattern.name, {})

    @property
    def wholeurl(self):
        return 'http://' + self.host + self.url

    @property
    def url_pattern(self):
        return self.url_patterns[-1:][0]

    def set_cookie(self):
        return

    @staticmethod
    def get_randobj_id(objname, noneable=False):
        if noneable:
            if random.random() * 2 < 1:
                return None
        model_class = ContentType.objects.get(name=objname, app_label__in=RequestSet.packages).model_class()
        id_max = model_class.objects.count()
        if not id_max:
            return True if noneable else ''
        randindex = random.randint(0, id_max - 1)
        return model_class.objects.all()[randindex].pk

    def gen_url(self):
        patternres = re.findall('\(\?P\<(.*?)\>.+?\)', self.url_pattern.regex.pattern)
        urlparams = {}
        ids_key = []
        for key in patternres:
            if key.endswith('_id'):
                urlparams[key] = self.get_randobj_id(key[:-3])
                ids_key.append(key)
            #else:
            #    urlparams[key] = rstr.xeger(self.url_pattern.regex.pattern)
        newpattern = self.url_pattern.regex.pattern
        for key in ids_key:
            for item in re.findall('\(\?P\<' + key + '\>.+?\)', self.url_pattern.regex.pattern):
                newpattern = newpattern.replace(item, '{' + key + '}')
        lasturl = newpattern.format(**urlparams)
        lasturl = rstr.xeger(lasturl)
        urls = []
        for p in self.url_patterns[:-1]:
            if type(p) == urlresolvers.RegexURLPattern:
                urls.append(rstr.xeger(p.regex.pattern))
            elif type(p) == urlresolvers.RegexURLResolver:
                urls.append(rstr.xeger(p._regex))
        urls.append(lasturl)
        self.url = ''.join(urls)
        if not self.url.startswith('/'):
            self.url = '/' + self.url

    def get_views(self):
        pass

    def get_whone_func_name(self):
        func, _callback_args, _callback_kwargs = self.resolver.resolve(
                            self.url)
        return '%s.%s' % (func.__module__, getattr(func, '__name__', func.__class__.__name__))

    def get_forms_method(self):
        from ..autodocs.views import import_module_without_decorators
        func_whole_name = self.get_whone_func_name()
        mod, func = urlresolvers.get_mod_func(func_whole_name)
        try:
            view_func = import_module_without_decorators(mod, func)
        except (ImportError, AttributeError):
            raise Http404
        forms = []
        module = import_module(mod)
        for var in view_func.func_code.co_names:
            if var.endswith('Form'):
                value = getattr(module, var)
                forms.append(value)
        method = 'POST' if 'POST' in view_func.func_code.co_names else 'GET'
        return forms, method

    def gen_params(self):
        custom_dict = {}
        direct_value = {}
        for key in self.urlconf.get('params', {}):
            if type(self.urlconf['params'][key]) == dict:
                if self.urlconf['params'][key].has_key('rand'):
                    custom_dict[key] = self.urlconf['params'][key]['rand']
                if self.urlconf['params'][key].has_key('value'):
                    if self.urlconf['params'][key]['value'] is None:
                        pass
                    elif self.urlconf['params'][key]['value'].startswith('randobj_'):
                        direct_value[key] = self.urlconf['params'][key]['value'][len('randobj_'):]
                    else:
                        direct_value[key] = self.urlconf['params'][key]['value']
            else:
                direct_value[key] = self.urlconf['params'][key]
        params = []
        forms, self.method=self.get_forms_method()
        for form in forms:
            params.append(form.gen_random_data(RandVar.RIGHT_LIMIT, custom_dict=custom_dict,direct_value=direct_value))
        res = {}
        for p, sign, error in params:
            if p:
                res.update(p) 
        self.params = res

    def gen_request(self):
        return

    def print_self(self):
        s = []
        for p in self.url_patterns:
            if type(p) == urlresolvers.RegexURLPattern:
                s.append(p.regex.pattern)
            elif type(p) == urlresolvers.RegexURLResolver:
                s.append(p._regex)
        log.info('Request URL ' + self.url_pattern.name + ':' + ''.join(s))

    def run(self):
        if self.urlconf.has_key('url'):
            self.url = self.urlconf['url']
        else:
            self.gen_url()
        self.gen_params()
        if self.method == "POST":
            if not self.dopost:
                log.info('post request pass')
                conn = None
            else:
                self.print_self()
                log.info('url post:' + self.url)
                log.info('params:' + json.dumps(self.params))
                conn = httplib.HTTPConnection(self.host)
        else:
            self.print_self()
            log.info('url:' + self.url)
            log.info('params:' + json.dumps(self.params))
            conn = httplib.HTTPConnection(self.host)
        if not conn:
            return
        headers = {'Content-Type': 'text/html',
                        'Vary': 'Cookie',
                        'Cookie': self.cookie
                        }
        params = urllib.urlencode(self.params)
        conn.request(self.method, self.url, params, headers)
        response = conn.getresponse()
        log.info('status_code:' + str(response.status))
        self.analysis_response(response.read(), response.status)
        conn.close()

    def analysis_response(self, response_str, response_status):
        if response_status == 200:
            res = None
            if self.method == "POST":
                try:
                    res = json.loads(response_str)
                except:
                    self.write_error_log(response_str, 'json')
                if res and 'status' in res and res['status'] == 0:
                    log.info('成功')
                else:
                    self.write_error_log(response_str, 'json')
            else:
                log.info('成功')
        else:
            self.write_error_log(response_str)

    def write_error_log(self, response, res_type='html'):
        filename = self.get_whone_func_name() + '.html'
        log.info('请求失败，错误信息参考' + filename)
        if res_type == 'json':
            template_path = os.path.join(os.path.join(os.path.dirname(__file__), 'template'), 'res_temp.html')
            ftemp = open(template_path)
            template_str = ftemp.read()
            ftemp.close()
            template = Template(template_str)
            response = template.render(Context({'errmessage': response}))
        f = open(os.path.join(self.logpath, filename), 'wb')
        f.write(response)
        f.close()
        return


class ReqTest(object):
    def __init__(self, conf):
        self.packages = conf.packages
        self.logpath = conf.logpath
        self.testright = conf.testright
        self.dopost = conf.dopost
        self.rollback = conf.rollback
        self.forbidcookie = conf.forbidcookie
        self.packages = conf.packages
        self.whitelist = conf.whitelist
        self.backlist = conf.backlist
        self.urlconf = conf.urlconf
        self.host = conf.host
        self.cookie = conf.cookie
        self.reqlogpath = os.path.join(self.logpath, 'errorlog_' + datetime.now().strftime('%Y%m%d%H%M%S'))
        os.makedirs(self.reqlogpath)
        RequestSet.packages = self.packages

    def gen_requests(self):
        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
        self.resolver = resolver
        res = []
        def resolve_patterns(patterns, ancestor=[]):
            for p in patterns:
                if type(p) == urlresolvers.RegexURLPattern:
                    req = RequestSet(ancestor + [p],self)
                    res.append(req)
                elif type(p) == urlresolvers.RegexURLResolver:
                    resolve_patterns(p.url_patterns, ancestor + [p])
        resolve_patterns(resolver.url_patterns)
        self.requests = []
        for item in res:
            if item.url_pattern.name:
                item.resolver = self.resolver
                skip = False
                for name_unmatch in self.backlist:
                    if item.url_patterns[0]._regex ==  name_unmatch or item.url_pattern.name == name_unmatch:
                        skip = True
                        break
                if skip:
                    continue
                for name_regex in self.whitelist:
                    if item.url_patterns[0]._regex ==  name_regex or re.compile(name_regex).match(item.url_pattern.name):
                        self.requests.append(item)
                        break

    def run(self):
        self.gen_requests()
        #log.info|log.info
        log.info('*****************************************************************************************************************')
        log.info(u'自动化请求模拟测试开始，本次共有' + str(len(self.requests)) + u'个请求需要模拟，当前时间是' + datetime.now().strftime('%Y-%m-%d '))
        for req in self.requests:
            req.run()
        log.info('*****************************************************************************************************************')

    def rollback(self):
        pass 