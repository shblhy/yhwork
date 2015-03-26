# -*- coding: utf-8 -*-
import json
'''
    重写Table提供给前端控件的json数据格式，依不同的数据类型，封装所需数据。
'''
from widget import Table
from collections import OrderedDict
from copy import copy

class OurTable(Table):
    total_page = 10
    total_num = 100
    def get_rows(self):
        rows = []
        tmpl = OrderedDict(self.columns+self.visible_columns)
        for line in self.rows:
            orderedItem = copy(tmpl)
            i = 0
            for key in orderedItem:
                orderedItem[key] = line[i]
                i = i+1
            rows.append(orderedItem)
        res = {
               'page_size':self.page_size,
               'page_num':self.page,
               'total_page':self.num_pages,
               'total_num':self.total,
               'result':rows
               }
        return json.dumps(res)