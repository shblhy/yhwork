#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
@author:hy
自动测试，只要研发遵循django标准，不需写任何测试代码即可进行测试
测试结果保存在logs/autotest.log当中
利用前后台接口信息（form）自动产生request,预期response，并比较实际结果与预期结果，两者有差异时，记录日志
扫描urls获取对应views，辨识views代码识别Form，利用Form生成Request，从而获得批量request
可以设定每个request是否进行数据回滚、是否只测试正确数据。
rollback 数据回滚
testright 尽量测正确数据（required=true的必然产生，field有validate的自动按照校验正则进行，但对自定义field无效，不保证必然产生正确数据）
times 测试次数
thread 模拟测试    用户数（未来实现）
forbidcookie 禁止自动cookie
-f requests.conf 
    在requests.conf中配置对每个request进行配置
    requests:
    whitelist
    backlist
    
    rollback
    params:{
        xx:{randgen:true  #randgen(随机决定是否生成本数据)
        randmode #随机数据数据描述
        }  
        par
    }
'''
class Abc(object):
    return
