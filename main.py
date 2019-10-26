1  # !/usr/bin/env python
2  # -*- coding: utf-8 -*-
3  # @Time  : 20:25
4  # @File  : main.py
5  # @Author: Ch
6  # @Date  : 2019/10/24
from sys import stdin

import util_m
from DataMining import apriori
from DataMining import fp_growth

if __name__ == '__main__':
    ftype = 0
    support, confidence = 0.0, 0.0
    print("请输入\n"
          "函数序号（1.Apriori 2.fpgrowth）\n"
          "支持度 置信度(0,1)\n"
          "文件名（文件位于res文件夹下）\n"
          "以空格分隔 如：“1 0.5 0.5 data2.json”，"
          "输入#退出")
    while True:
        print("请输入命令：")
        inputdata = stdin.readline().split(" ")
        # print(inputdata)
        if inputdata == ['#\n']:
            break
        if len(inputdata) < 4:
            continue
        ftype = inputdata[0]
        if ftype != "1" and ftype != "2":
            print("函数序号格式有误，请重试")
            continue
        try:
            support = float(inputdata[1])
            confidence = float(inputdata[2])
        except ValueError:
            support = 0
            confidence = 0
            print("输入有误,请重试")
            continue
        try:
            path = inputdata[3].split("\n")[0]
            data = util_m.read_data('res/%s' % path)
        except FileNotFoundError:
            print("文件名有误，请重试")
            continue
        if ftype == "1":
            apr = apriori.Apriori(datas=data, support=support, confidence=confidence)
            print(apr.freq_set)
            print(util_m.relate_rules2str(apr.rel_rules))
        else:
            fp = fp_growth.FPGrowth(datas=data, support=support, confidence=confidence)
            print("频繁模式树为：")     
            fp.fp_tree_root_point.print()
            print("频繁项集",fp.freq_set)
            print(util_m.relate_rules2str(fp.relate_rule))
            print()
