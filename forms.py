#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
@author:hy 
扩展 django的form，更好地获取参数
可获取其validator正则
"""
import os
from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils.encoding import  force_unicode
from django.forms import models
from django.core import validators
from django.utils import formats
from django.utils.translation import ugettext_lazy as _


'''
class MyErrorList(list, StrAndUnicode):
    """
    A collection of errors that knows how to display itself in various formats.
    """
    def __unicode__(self):
        return ''.join([force_unicode(e) for e in self])

    def as_text(self):
        if not self: return u''
        return u'\n'.join([u'* %s' % force_unicode(e) for e in self])

    def __repr__(self):
        return repr([force_unicode(e) for e in self])
    
    def errors_as_text(self):
        errorList = [u'* %s(%s)%s' % (self.fields[k].label,k, v) for k, v in self.errors.items()] 
        return u'\n'.join(errorList)
'''
    
class ExtendBaseForm(object):
    
    def errors_as_text(self):
        errorList = [u'* %s(%s)%s' % (self.fields[k].label,k, v) for k, v in self.errors.items()] 
        return u'\n'.join(errorList)
    
    def errors_as_json(self):
        return [(self.fields[k].label,k, v) for k, v in self.errors.items()]
    
    @classmethod
    def get_model_field(cls,field):
        if issubclass(cls,models.ModelForm):
            return cls.Meta.model._meta.get_field_by_name(field)[0]
        return None
    
    @classmethod
    def gen_random_data(cls,mode = 1,custom_dict={},direct_value={}):
        from request_gen import get_random_data
        values = {}
        if issubclass(cls,models.ModelForm):
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    model_field = cls.get_model_field(key)
                    values[key] = get_random_data(field,custom_dict.get(key,mode),model_field)
        else:
            for key in cls.base_fields:
                if key in direct_value:
                    if not direct_value[key] is None:
                        values[key] = direct_value[key]
                else:
                    field = cls.base_fields[key]
                    values[key] = get_random_data(field,mode= custom_dict.get(key,mode))
        form = cls(values)
        res = form.is_valid()
        return values,res,form.errors_as_json()
   
    @classmethod
    def as_desc(cls):
        '''返回表单描述'''
        '''
        品牌（brand）（查询）表单
        ID    id    描述    限制/正则
        ID    id    描述    限制/正则
        '''
        from django.template import Context,Template
        from django.template.loader import get_template
        def to_str(value):
            return '' if value is None else unicode(value)
        def get_name(key,field):
            return key.upper() if field.label is None else field.label
        def get_desc(field):
            if isinstance(field,forms.IntegerField):
                return u'整型'
            elif isinstance(field,forms.CharField):
                return u'字符串'
            elif isinstance(field,forms.ChoiceField):
                if not isinstance(field,models.ModelChoiceField):
                    choice_str = ','.join([str(k)+':'+str(v) for k,v in field.choices[:20] if k])
                    if len(field.choices)>20:
                        choice_str += u'等等'
                    return u'枚举('+choice_str+')'
                return u'枚举(值来自数据库)'
            elif isinstance(field,forms.DateTimeField):
                return u'日期'
            else:
                return field.__class__.__name__
        cls_name = cls.__name__
        if issubclass(cls,models.ModelForm):
            cls_name = cls_name +' | '+ to_str(cls.Meta.model._meta.verbose_name) + u'表单'
        cls_doc = cls.__doc__
        field_list = []
        for key in cls.base_fields:
            field = cls.base_fields[key]
            item = {}
            item['label'] = get_name(key,field)
            item['key'] = key
            item['is_required'] = u'必填' if field.required else u'选填'
            if hasattr(field,'default'):
                item['is_required'] = item['is_required'] + '(默认为'+str(field.default)+')'
            item['desc'] = get_desc(field)
            field_list.append(item)
        template_path = os.path.join(os.path.join(os.path.dirname(__file__),'template'),'form_desc.html')
        template_file = open(template_path)
        template_content = template_file.read()
        template_file.close()
        template = Template(template_content)
        #template = get_template(template_path)
        return template.render(Context(locals()))
    
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
        kwargs['label'] = kwargs.get('label','')
        kwargs['min_value'] = 0
        super(PageField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(PageField, self).to_python(value)
        if value is None:
            value = self.default
        return value


class Form(forms.Form,ExtendBaseForm):
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


class BigIntegerField(forms.Field):
    default_error_messages = {
        'invalid': _(u'Enter a whole number.'),
        'max_value': _(u'Ensure this value is less than or equal to %(limit_value)s.'),
        'min_value': _(u'Ensure this value is greater than or equal to %(limit_value)s.'),
    }

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        super(BigIntegerField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def to_python(self, value):
        """
        Validates that int() can be called on the input. Returns the result
        of int(). Returns None for empty values.
        """
        value = super(BigIntegerField, self).to_python(value)
        if value in validators.EMPTY_VALUES:
            return None
        if self.localize:
            value = formats.sanitize_separators(value)
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])
        return value
