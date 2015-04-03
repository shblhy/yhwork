# -*- coding: utf-8 -*-
'''
内容管理（列表数据容器），实现列表内容到json的转换以适应前端控件要求。
'''
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import MultipleObjectMixin
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.forms.models import fields_for_model
from django.template.loader import get_template, Context
from django.db.models import AutoField
from widget import Table


def ignore_minus(s):
    if s.startswith('-'):
        return s[1:]
    return s


def check_order_bys(s, order_bys):
    for item in s.split(','):
        if not ignore_minus(item) in order_bys:
            return False
    return True


class OutManager(object):
    """
    目标：将数据转变为json等常规格式，以提供给前端处理。
    原计划模拟View编写，可同时处理django orm与sqlalchemy等多种格式数据，但考虑到开发难度目前只支持Model。
    from django.views.generic.base import View
    """
    # 需要产生的域，例如表格头行数据
    fields = []
    # 在界面不可见的域，注意在前端需要控件支持
    visible_fields = []
    # 准许排序的域
    order_fields = []
    # 域取值办法，如'attr1':lambda x: x.get_status_display() 其中x为该行model
    accessors = {}
    # 域回调办法，当需要外部参数传入时使用，也可以用于传入外部参数以进行表级处理。
    accessors_out = {}
    OUT_CALL = 'accessors_out'
    # 域名称，如果此处未定义则取model的verbose_name
    labels = {}
    # 分页器
    paginator_class = Paginator
    # 默认的表格控件
    table_class = Table
    # 数据暂存
    _data_cache = None
    exclude = []
    # 接收外部排序
    order_by = None
    # 默认排序方式
    default_order_by = None


class BaseListManager(MultipleObjectMixin, OutManager):
    '''列表数据容器'''
    object_list = []

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def paginate_queryset(self, queryset, page_size):
        """
        分页
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        try:
            page_number = int(self.page)
        except ValueError:
            raise Http404(_(u"参数page无法转化为正确页码"))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404(_(u'无效页码(%(page_number)s)') % {
                                'page_number': page_number
            })

    @property
    def data(self):
        if self._data_cache is None:
            self._data_cache = self.get_context_data(object_list=self.get_queryset())
        return self._data_cache

    def get_order_by(self):
        if self.order_by and check_order_bys(self.order_by):
            return self.order_by
        return self.default_order_by

    def get_line(self, item, excludes=[]):
        '''
        将对象转变为行输出
        通过get_line与accessors配合完成行级操作
        '''
        line = []
        try:
            for field in self.fields:
                if field in excludes:
                    continue
                func = self.accessors.get(field, None)
                if  func == OutManager.OUT_CALL:
                    func = self.accessors_out[field]
                if func:
                    attr = func(item)
                elif type(item) != dict:
                    attr = getattr(item, field)
                    if type(attr) == datetime:
                        attr = attr.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    attr = item.get('field', '')
                line.append(attr)
        except Exception, e0:
            raise e0
        return line

    def get_rows_data(self):
        '''表级处理，重写此方法以完成自定义的表级操作'''
        return [self.get_line(item) for item in self.data['object_list']]

    @property
    def objs(self):
        return self.data['object_list']

    def to_table(self, **kwargs):
        table_args = {
                      '_manager_': type(self),
                      '_manager_class_': self,
                      'rows': self.get_rows_data(),
                      'page_size': self.paginate_by,
                      'page': self.page,
                      'total': self.data['paginator'].count,
                      'num_pages': self.data['paginator'].num_pages,
                      }
        table_args.update(kwargs)
        return self.table_class(**table_args)

    @classmethod
    def to_empty_table(cls):
        table_args = {
                      '_manager_class_': cls,
                      'rows': [],
                      'page_size': cls.paginate_by,
                      'page': 1,
                      'total': 0,
                      'num_pages': 0,
                      }
        return cls.table_class(**table_args)

    def to_chart(self):
        pass

    def to_select(self):
        return

    @classmethod
    def get_field_labels(cls):
        '''
            返还域数组，形如[(field,label),]
        '''
        return [(field, cls.field_label(field)) for field in cls.fields]

    @classmethod
    def field_label(cls, field):
        if not hasattr(cls, 'base_fields'):
            cls.base_fields = fields_for_model(cls.model, cls.fields, [],  None, None)
            '''AutoField djangoform并未为其产生formfield'''
            for f in cls.model._meta.fields:
                if type(f) == AutoField:
                    f.label = f.verbose_name
                    cls.base_fields[f.name] = f
        if field in cls.labels:
            return cls.labels[field]
        if (field in cls.base_fields and cls.base_fields[field] is not None):
            return unicode(cls.base_fields[field].label)
        return unicode(field)

    @property
    def limit_begin(self):
        return (self.page - 1) * self.paginate_by

    def get_limit_str(self, db_type='mysql'):
        if db_type == 'mysql':
            return ' limit ' + str(self.limit_begin) + ',' + str(self.paginate_by)
        elif db_type == 'postgresql':
            return ' limit ' + str(self.paginate_by) + ' offset ' + str(self.limit_begin)
        else:
            return ' limit ' + str(self.paginate_by) + ' offset ' + str(self.limit_begin)

    @classmethod
    def as_desc(cls, tmpl='listmanager_desc.html'):
        '''返回数据描述'''
        '''
        域声明：['域名':'域中文名']
        内容声明：
            数据容器：[ModelClass(对象)]
            设置说明：分页/可排序域/排序设定
        输出声明：(输出必须有转化对象，默认为self.table_class)
            友好json
        '''
        if tmpl == 'rst':
            tmpl = 'listmanager_desc.rst'
        cls_base_name = cls_name = cls.__name__
        def to_str(value):
            return '' if value is None else unicode(value)
        if issubclass(cls, BaseListManager):
            cls_name = cls_name + ' | ' + to_str(cls.model._meta.verbose_name) + u'列表管理'
        cls_doc = cls.__doc__
        cls_model_name = cls.model.__name__
        cls_model_label = '(' + unicode(cls.model._meta.verbose_name) + ')' if unicode(cls.model._meta.verbose_name) else ''
        field_list = cls.get_field_labels()
        output_str = cls.to_empty_table().get_rows()
        template = get_template(tmpl)
        return template.render(Context(locals()))
