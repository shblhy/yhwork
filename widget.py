# -*- coding: utf-8 -*-
'''
    提供给前端控件的json数据格式，依不同的数据类型，封装所需数据。
    控件示例：控件名称#官网或作者
'''
import json
try:
    from settings import FRONT_BASE,FRONT_JS_TABLE,FRONT_JS_SELECT
except:
    FRONT_TABLE = 'base'
    #FRONT_TABLE = 'DataTables#www.datatables.net'
    #FRONT_TABLE = 'ShowTableData#chen'
    #FRONT_JS_SELECT = 'Select2'


class Widget(object):
    '''工具接收任何传入值作为其属性'''
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class BaseTable(Widget):
    rows = []
    columns = []
    page = 0
    page_size = 100

    def get_rows(self):
        '''获取数据内容'''
        return json.dumps(self.rows)

    def get_custom_rows(self, columns):
        '''获取指定域的数据'''
        using_indexs = [self.columns.index((col, coltext)) for col, coltext in self.columns if col in columns]
        return [[line[i] for i in sorted(using_indexs)] for line in self.rows]

    def get_columns(self):
        '''获取表格头行'''
        return json.dumps(self.columns)

    @property
    def columns_exclude_action(self):
        '''获取表格头行，但“操作”单元格除外'''
        columns = dict(self.columns).keys()
        columns.remove('action')
        return columns


class TableDataTables(BaseTable):
    def get_columns(self):
        return json.dumps([{'name': item[0], 'value': item[1], 'visible': item[1] in self.visible_fields} for item in self.columns.items()])

TABLE_CLASSES = {
                 'base': BaseTable,
                 'DataTables': TableDataTables,
                 }
Table = TABLE_CLASSES[FRONT_TABLE.split('#')[0]]


class Select(Widget):
    pass
