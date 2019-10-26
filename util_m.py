1  # !/usr/bin/env python
2  # -*- coding: utf-8 -*-
3  # @Time  : 11:41
4  # @File  : util_m.py
5  # @Author: Ch
6  # @Date  : 2019/10/23
import json


def read_data(path):
    with open(path) as res:
        data = json.load(res)
        return data


def relate_rules2str(relate_rules: dict):
    """
    打印关联规则
    :param relate_rules:
    """
    str_res = "关联规则为{"
    # print("关联规则为{",end='')
    for rule in relate_rules.keys():
        str_pre = ""
        for item in rule:
            str_pre += str(item)
        str_suf = ""
        for item in relate_rules[rule]:
            str_suf += str(item)
        # print(" %s:%s;" % (str_pre, str_suf),end="")
        str_res += "%s:%s; " % (str_pre, str_suf)
    str_res+="}"
    # print("}",end='')
    return str_res
