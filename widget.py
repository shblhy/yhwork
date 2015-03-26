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
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
            
            
class Table(Widget):
    rows = []
    columns = []
    page = 0
    page_size = 100
    
    def get_rows(self):
        return json.dumps(self.rows)
        
    
    def get_custom_rows(self,columns):
        using_indexs = [self.columns.index((col,coltext)) for col,coltext in self.columns if col in columns]
        return [[line[i] for i in sorted(using_indexs)] for line in self.rows]
    
    def get_columns(self):
        return json.dumps(self.columns)
    
    def get_all(self):
        res = {}
        return json.dumps(res)
    
    @property
    def tmpl(self):
        return {}
    
    def to_csv(self):
        columnsDict = dict(self.columns)
        return self.get_custom_rows(columns=self.columns_exclude_action),[columnsDict[c] for c in self.columns_exclude_action]
    
    @property
    def columns_exclude_action(self): 
        columns = dict(self.columns).keys()
        columns.remove('action')
        return columns
    
    
    
class BaseTable(Table):
    pass

class TableDataTables(Table):
    def get_columns(self):
        return json.dumps([{'name':item[0],'value':item[1]} for item in self.columns.items()])
    
TABLE_CLASSES = {
                 'base':BaseTable,
                 'DataTables':''
                 }
Table = TABLE_CLASSES[FRONT_TABLE]

class Select(Widget):
    pass