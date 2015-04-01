# -*- coding: utf-8 -*-
'''
内容管理，实现内容到json的转换以适应前端控件要求。
'''
import unittest
import re
from datetime import datetime
from random_gen import RandVar
from request_gen import RequestSet, ReqTest

from dowant.cart.forms import FailedOrderQForm, FailedOrderRestaurantQForm, FailedRestaurantOrderDetailQForm


class FailedOrderQFormTest(unittest.TestCase):
    def runTest(self):
        #test_form_gen_data()
        test_req_test()
        print 'end'


def test_form_gen_data():
    data = FailedOrderQForm.gen_random_data(RandVar.RIGHT_LIMIT)[0]
    form = FailedOrderQForm(data)
    if form.is_valid():
        print 'valid success!'
        return
    else:
        print 'valid failed:'
    print data
    print form.errors_as_text()


def test_req_test():
    from . import autotestconf
    req = ReqTest(autotestconf)
    req.run()
