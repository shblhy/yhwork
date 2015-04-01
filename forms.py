#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
@author:hy
扩展 django的form，更好地获取参数
可获取其validator正则
"""
import os
from django import forms
from django.forms import models
from .fields import PageField


class ExtendBaseForm(object):
    def errors_as_text(self):
        errorList = [u'* %s(%s)%s' % (self.fields[k].label, k, v.as_text()) for k, v in self.errors.items()]
        return u'\n'.join(errorList)

    def errors_as_json(self):
        return [(self.fields[k].label, k, v.as_text()) for k, v in self.errors.items()]

    @classmethod
    def get_model_field(cls, field):
        if issubclass(cls, models.ModelForm):
            return cls.Meta.model._meta.get_field_by_name(field)[0]
        return None

    @classmethod
    def gen_value_dict(cls, mode=1, custom_dict={}, direct_value={}):
        from .autotest.request_gen import get_random_data
        values = {}
        if issubclass(cls, models.ModelForm):
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    model_field = cls.get_model_field(key)
                    values[key] = get_random_data(field, custom_dict.get(key, mode), model_field)
        else:
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    values[key] = get_random_data(field, mode=custom_dict.get(key, mode))
        return values

    @classmethod
    def gen_random_data(cls, mode=1, custom_dict={}, direct_value={}):
        from .autotest.request_gen import get_random_data
        values = {}
        if issubclass(cls, models.ModelForm):
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    model_field = cls.get_model_field(key)
                    values[key] = get_random_data(field, custom_dict.get(key, mode), model_field)
        else:
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    values[key] = get_random_data(field, mode=custom_dict.get(key, mode))
        form = cls(values)
        res = form.is_valid()
        return values, res, form.errors_as_json()

    @classmethod
    def as_desc(cls):
        '''返回表单描述'''
        '''
        品牌（brand）（查询）表单
        ID    id    描述    限制/正则
        ID    id    描述    限制/正则
        '''
        from django.template import Context, Template
        from django.template.loader import get_template
        def to_str(value):
            return '' if value is None else unicode(value)
        def get_name(key,field):
            return key.upper() if field.label is None else field.label
        def get_desc(field):
            if isinstance(field, forms.IntegerField):
                return u'整型'
            elif isinstance(field, forms.CharField):
                return u'字符串'
            elif isinstance(field, forms.ChoiceField):
                if not isinstance(field, models.ModelChoiceField):
                    choice_str = ','.join([str(k) + ':' + str(v) for k, v in field.choices[:20] if k])
                    if len(field.choices) > 20:
                        choice_str += u'等等'
                    return u'枚举(' + choice_str + ')'
                return u'枚举(值来自数据库)'
            elif isinstance(field, forms.DateTimeField):
                return u'日期'
            else:
                return field.__class__.__name__
        cls_name = cls.__name__
        if issubclass(cls, models.ModelForm):
            cls_name = cls_name + ' | ' + to_str(cls.Meta.model._meta.verbose_name) + u'表单'
        cls_doc = cls.__doc__
        field_list = []
        for key in cls.base_fields:
            field = cls.base_fields[key]
            item = {}
            item['label'] = get_name(key, field)
            item['key'] = key
            item['is_required'] = u'必填' if field.required else u'选填'
            if hasattr(field, 'default'):
                item['is_required'] = item['is_required'] + u'(默认为' + str(field.default) + ')'
            item['desc'] = get_desc(field)
            field_list.append(item)
        template = get_template('form_desc.html')
        return template.render(Context(locals()))


class Form(forms.Form, ExtendBaseForm):
    pass


class QForm(Form):
    page = PageField(default=1, label=u'页数')
    page_size = PageField(default=20, label=u'每页记录数')
    order_by = forms.CharField(label=u'排序', required=False)
    TABLE_KEYS = ['page', 'page_size', 'page_num', 'page_length',
                   'order_by', 'iDisplayStart', 'iDisplayLength', 'orderBy']

    def get_conditions(self):
        '''遍历form所有字段，如果cleaned_data存在它，则它作为数据库查询条件'''
        conditions = {}
        for key in self.cleaned_data:
            if not key in QForm.TABLE_KEYS and self.cleaned_data.get(key):
                conditions[key] = self.cleaned_data[key]
        return conditions


class ModelForm(models.ModelForm, ExtendBaseForm):
    pass
