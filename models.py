#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
@author:hy 
扩展 django的model，将model方便地转化为json
"""
from datetime import datetime
from django.core import validators
from django.db.models.fields import CharField


class MysqlEncryField(CharField):

    def __init__(self, *args, **kwargs):
        self.encry_method = kwargs.pop('encry_method')
        self.encry_key = kwargs.pop('encry_key')
        super(MysqlEncryField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_placeholder(self, val, connection):
        if val:
            return r"{encry_method}(%s, '{encry_key}')".format(encry_method='AES_ENCRYPT',
                                                               encry_key=self.encry_key)
        return '%s'


class JsonParser(object):
    @classmethod
    def accessors(cls):
        return {
                 }

    @classmethod
    def get_field_map(cls):
        res = {}
        for field in cls._meta.fields:
            res[field.name] = field.db_column
        return res

    def to_json(self, fields=[], time_to_str=True, bool01=True):
        if fields:
            show_fields = fields
        else:
            show_fields = [field.attname for  field in self._meta.fields]
        res = {}
        for field in show_fields:
            func = self.accessors().get(field, None)
            if func:
                res[field] = func(self)
            else:
                res[field] = func(self) if func else getattr(self, 'get_' + field + '_display')() \
                    if hasattr(self, 'get_' + field + '_display') else getattr(self, field)
            if time_to_str and type(res[field]) == datetime:
                res[field] = res[field].strftime('%Y-%m-%d %H:%M:%S')
            if bool01 and type(res[field]) == bool:
                res[field] = int(res[field])
        return res
