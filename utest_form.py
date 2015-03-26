# -*- coding: utf-8 -*-
'''
内容管理，实现内容到json的转换以适应前端控件要求。
'''
import unittest
from django.contrib.auth.models import User
from apps.client.models import City
from apps.client.forms import StoreForm,VisitQForm,BrandForm,BrandQForm
from apps.form.models import Project,Network,Contact,ContractInfo
from datetime import datetime
from random_gen import RandVar
from request_gen import RequestSet,ReqTest
from wiwidebd.libs.com import autotestconf
import re
class ProjectTest(unittest.TestCase):
    def runTest(self):
        #p = re.compile('[\d]{5}')
        #print p.match('55')
        #print test_request()
        test_print_url()
        #s= test_form_gen_data()
        #print s[0]
        #print s[1]
        #print s[2]
        
    
def test_form_gen_data():
    return BrandQForm.gen_random_data(RandVar.RIGHT_LIMIT)
#url(r'^brand/(?P<brand_id>[\d]+)/detail$', 'views_brand.brand_detail', name="brand_detail_html"),

def test_request():
    r = RequestSet('/form/contacts',{})
    r.run()
    
def test_print_url():
    a= ReqTest(autotestconf)
    a.gen_requests()
    print len(a.requests)
    for req in a.requests:
        req.run()