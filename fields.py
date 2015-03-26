# -*- encoding: utf-8 -*-
#@author: 黄炎 
'''
1、forms.CharField将外部传入的值都变为''，在null=True时不一定合适，在unique=True时引发异常。为此新增加了DefaultCharField,DefaultIntegerField
2、PageField
'''
from django import forms


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