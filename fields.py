# -*- encoding: utf-8 -*-
#@author: 黄炎
'''
1、forms.CharField将外部传入的值都变为''，在null=True时不一定合适，在unique=True时引发异常。为此新增加了DefaultCharField,DefaultIntegerField
2、PageField
'''
from django import forms
from .admin import check_order_bys
from django.core.exceptions import ValidationError


class DefaultCharField(forms.CharField):
    '''
    具备默认值的field，当前端未传入值或传入无效值时该域值自动设为默认值
    '''
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = None
        kwargs['widget'] = forms.HiddenInput
        kwargs['required'] = False
        kwargs['label'] = ''
        super(DefaultCharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(DefaultCharField, self).to_python(value)
        if value is None:
            value = self.default
        return value


class DefaultIntegerField(forms.IntegerField):
    '''
    具备默认值的field，当前端未传入值或传入无效值时该域值自动设为默认值
    '''
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = 0
        kwargs['widget'] = forms.HiddenInput
        kwargs['required'] = False
        kwargs['label'] = ''
        kwargs['min_value'] = 0
        super(DefaultIntegerField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(DefaultIntegerField, self).to_python(value)
        if value is None:
            value = self.default
        return value


class PageField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = 0
        kwargs['widget'] = forms.HiddenInput
        kwargs['required'] = False
        kwargs['label'] = kwargs.get('label', '')
        kwargs['min_value'] = 0
        super(PageField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(PageField, self).to_python(value)
        if value is None:
            value = self.default
        return value


class OrderByField(forms.CharField):
    order_bys = []

    def __init__(self, *args, **kwargs):
        self.order_bys = kwargs.pop('order_bys', self.order_bys)
        self.max_length = 200
        kwargs['required'] = False
        super(forms.CharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = forms.CharField.to_python(self, value)
        if value and not check_order_bys(value, self.order_bys):
            errmsg = u'排序域只能在<' + ','.join(self.order_bys) + u'>中选，以,联结，允许加-表示倒序，请检查'
            raise ValidationError(errmsg)
        return value
