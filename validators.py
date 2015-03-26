# -*- encoding: utf-8 -*-
'''
    @author:hy 
    phone,fixed_phone,qq的校验
'''
import re

from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

phone_re = re.compile(r'^[0-9]{5,25}$')
validate_phone = RegexValidator(phone_re, _(u'手机号码为5-25位纯数字.'), 'invalid')

fixed_phone_re = re.compile(r'^[-|0-9]{5,25}$')
validate_fixed_phone = RegexValidator(fixed_phone_re, _(u'座机号码为5-25位数字，可用-分隔.'), 'invalid')

qq_re = re.compile(r'^[1-9][0-9]{4,}$')
validate_qq = RegexValidator(qq_re, _(u'腾讯QQ号从10000开始.'), 'invalid')
