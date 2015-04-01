# -*- encoding: utf-8 -*-
'''
@author:hy
随机数据生成器，生产随机测试数据供自动化测试使用。
使用了rstr（Copyright (c) 2011, Leapfrog Direct Response, LLC）以生产随机字串，部署考虑直接将其源码复制至此。
'''
import random
import rstr
from datetime import datetime, timedelta

TYPE_A = ['num','string']
TYPE_NUM = ['int','float','long','complex']
TYPE_STRING = ['astr','cstr','regex','rstr']
TYPE_RSTR = ['digits','domainsafe','letters','lowercase','nondigits','nonletters','nonwhitespace','nonword','normal','postalsafe','printable','punctuation','uppercase','urlsafe','whitespace','word']


class RandVar(object):
    '''本类用于解析变量类型(mode)描述。
        变量描述
        int
        notins_float
        int表示该变量为int型，notins 为 not instance的缩写，即不是该类型的实例
        num 包含 int float long 三种类型 (不支持complex)
        string 包含cstr regex rstr_xx四种类型  另外astr等同为rstr_printable 即可输入的任意字符
        rstr_xx这里的xx可以为
        'digits','domainsafe','letters','lowercase','nondigits','nonletters','nonwhitespace','nonword','normal','postalsafe','printable','punctuation','uppercase','urlsafe','whitespace','word' 这些rstr的简便方法
        datetime 包含 time time_1_month
        为了便于编译器理解（你可以.出来），将这些大写，直接作为RandVar的静态变量
        高级扩展（肯定.不出来^_^） 比较：gt lt et bet
        gt 即greater than 大于 lt 即 less than 小于 gte 即大于等于
        bet为两者之间（含等于），此时param为元组
        随机都有范围，默认类型与范围值如下：
        类型 gt极值 lt极值
        int 65536 -65536
        float 1024.0 -1024.0
        long 134217728 -134217728
        允许自定义mode，形如int_lt_0,float_lt_1,这种写法不支持notins
        高级扩展（肯定.不出来^_^）  组合：
        int_float 表述int与float，不允许用带包含关系的两者，例如int_num是错误的。
        编码成本原因暂时不对string实现高级扩展
    '''
    RIGHT_LIMIT = 1
    #-----------------
    NUM = 'num'
    NOTINS_NUM = 'notins_num'
    STRING = 'string'
    NOTINS_STRING = 'notins_string'
    INT = 'int'
    NOTINS_INT = 'notins_int'
    FLOAT = 'float'
    NOTINS_FLOAT = 'notins_float'
    LONG = 'long'
    NOTINS_LONG = 'notins_long'
    COMPLEX = 'complex'
    NOTINS_COMPLEX = 'notins_complex'
    ASTR = 'astr'
    NOTINS_ASTR = 'notins_astr'
    CSTR = 'cstr'
    NOTINS_CSTR = 'notins_cstr'
    REGEX = 'regex'
    NOTINS_REGEX = 'notins_regex'
    RSTR = 'rstr'
    NOTINS_RSTR = 'notins_rstr'
    DIGITS = 'rstr_digits'
    DOMAINSAFE = 'rstr_domainsafe'
    LETTERS = 'rstr_letters'
    LOWERCASE = 'rstr_lowercase'
    NONDIGITS = 'rstr_nondigits'
    NONLETTERS = 'rstr_nonletters'
    NONWHITESPACE = 'rstr_nonwhitespace'
    NONWORD = 'rstr_nonword'
    NORMAL = 'rstr_normal'
    POSTALSAFE = 'rstr_postalsafe'
    PRINTABLE = 'rstr_printable'
    PUNCTUATION = 'rstr_punctuation'
    UPPERCASE = 'rstr_uppercase'
    URLSAFE = 'rstr_urlsafe'
    WHITESPACE = 'rstr_whitespace'
    WORD = 'rstr_word'
    DEFAULT_STR = 'rstr_letters'

    #常用字符
    CN_WORD = 'regex', ur'[\u4e00-\u9fa5]{1,8}'
    INT_GT_0 = 'int_gt_0', None
    ASTR = 'rstr_printable', None
    TIME = 'time', 7 * 24 * 60 * 60
    TIME_B_1_WEEK = 'time', 7 * 24 * 60 * 60

    @staticmethod
    def shortcuts():
        return [RandVar.CN_WORD, RandVar.INT_GT_0, RandVar.ASTR, RandVar.TIME]

    @staticmethod
    def print_self_constant():
        for s in TYPE_A + TYPE_NUM + TYPE_STRING:
            print (s).upper() + ' = \'' + (s) + '\''
            print ('notins_' + s).upper() + ' = \'' + ('notins_' + s) + '\''
        for s in TYPE_RSTR:
            print (s).upper() + ' = \'' + ('rstr_' + s) + '\''

    @staticmethod
    def parse_mod(mode):
        '''检查模式，返回类型type_need及标志语sign，如果类型为rstr，则调用resr.sign指向的方法，如果类型为gt lt et则必有参数Param依据param生成相应值
        return type_need,sign,param,notins
        '''
        types = TYPE_A + TYPE_NUM + TYPE_STRING + TYPE_RSTR
        type_need = None
        sign = None
        notins = False
        param = None
        if mode.startswith('notins_'):
            notins = True
            mode = mode[len('notins_'):]
        modeitems = mode.split('_')
        if not modeitems[0] in types:
            raise Exception(u'无效的随机数据类型描述')
        if modeitems[0] in TYPE_STRING + TYPE_RSTR:
            type_need = 'rstr'
            if len(modeitems) == 1:
                if modeitems[0] == 'cstr':
                    sign = 'rstr'
                elif modeitems[0] == 'regex':
                    sign = 'xeger'
            elif len(modeitems) == 2:
                sign = modeitems[1]
        elif modeitems[0] in TYPE_NUM:
            type_need = eval(modeitems[0])
            if len(modeitems) > 1:
                if modeitems[1] in ['gt', 'lt', 'et', 'lte']:
                    sign = modeitems[1]
                    param = type_need(modeitems[2])
                elif modeitems[1] == 'bet':
                    sign = modeitems[1]
                    param = (type_need(modeitems[2]), type_need(modeitems[3]))
        return type_need, sign, param, notins

    @staticmethod
    def get_type_desc(mode):
        '''获取类型'''
        t = RandVar.check_mod(mode)
        if not t:
            return RandVar.RIGHT_LIMIT
        return t

    @staticmethod
    def gen_data(mode, regex_param=None):
        '''
        解析mode，获取类型、参数
        regex_exprs 允许为None,正则字串
        支持多正则，多正则时直接加()并用|分隔正则即可
        生成参数
        '''
        if mode in RandVar.shortcuts():
            mode, regex_param = mode[0],mode[1]
            if mode == 'time':
                randsec = random.randint(0, regex_param)
                return (datetime.now() - timedelta(seconds=randsec)).strftime('%Y-%m-%d %H:%M:%S')
        limits = {
                  int:{'low_limit':-65536,'high_limit':65536,'function': lambda x:random.randrange(x[0],x[1])},
                  float:{'low_limit':-1024.0,'high_limit':1024.0,'function': lambda x:random.random()*(x[1]-x[0])+x[0]},
                  long:{'low_limit':-134217728,'high_limit':134217728,'function': lambda x:random.randrange(x[0],x[1])}
                  }
        type_need,sign,param,notins = RandVar.parse_mod(mode)
        if notins:
            #随机选择一种不为type_need的数据类型
            assert u'待实现'
        if type_need in [int,float,long]:
            if sign == 'et':
                return param

            low_limit = limits[type_need]['low_limit']
            high_limit = limits[type_need]['high_limit']
            if sign == 'gt':
                low_limit = param
            elif sign == 'lt':
                high_limit = param
            this_limit = low_limit,high_limit
            return limits[type_need]['function'](this_limit)
        elif sign == 'xeger':
            return rstr.xeger(regex_param)
        elif sign == 'cstr':
            return rstr.rstr(**regex_param)
        elif type_need == 'rstr':
            return eval(type_need+'.'+sign)()
        elif type_need == 'datetime':
            return datetime.now()


if __name__ == '__main__':
    RandVar.print_self_constant()
    print RandVar.gen_data(RandVar.INT)
    print RandVar.gen_data(RandVar.INT_GT_0)
    print RandVar.gen_data('float_lt_0')
    print RandVar.gen_data('int_gt_0')
    print RandVar.gen_data('rstr_digits')
    print RandVar.gen_data('rstr_lowercase')
    print RandVar.gen_data(RandVar.CN_WORD)