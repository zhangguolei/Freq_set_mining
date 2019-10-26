1  # !/usr/bin/env python
2  # -*- coding: utf-8 -*-
3  # @Time  : 23:07
4  # @File  : DataMining.py
5  # @Author: Ch
6  # @Date  : 2019/10/19
import json
import util_m


class Apriori:

    def __init__(self, datas: dict, support, confidence):
        """
        类构造函数
        :param datas:数据集{记录名：项目集}
        :param support: 最小支持度
        :param confidence: 最小置信度
        """
        self.__freq_set = {}
        self.__relate_rule = {}
        count_datas = len(datas.keys())
        self.support_num = int(support * count_datas)
        self.confidence = confidence
        # 初始化单个数据项
        item_set = {}
        for record in datas.values():
            for item in record:
                if (item,) in item_set.keys():
                    item_set[(item,)] += 1
                else:
                    item_set[(item,)] = 1
        # 频繁一项集
        temp_freq_set = self.get_freq_items(item_set, self.support_num)
        # print(temp_freq_set)
        # 添加到结果
        for k, v in temp_freq_set.items():
            self.__freq_set[k] = v

        # 循环查询频繁项集
        while len(temp_freq_set) > 1:
            item_set = self.generate_next_level(temp_freq_set)  # 连接
            # print(item_set)
            item_set = self.cut_tree(item_set)  # 剪枝
            # print(item_set)
            temp_freq_set = self.get_freq_items(self.count_freq_item(datas, item_set), self.support_num)  # 计算频度取频繁项集
            # print(temp_freq_set)
            # 添加到结果
            for k, v in temp_freq_set.items():
                self.__freq_set[k] = v


        #  完成频繁项集查找 接下来获取关联规则
        for item_group in self.__freq_set.keys():
            if len(item_group) == 1:
                continue
            else:
                data = [i for i in item_group]  # 一个频繁项集
                rules = self.__cal_rel_rule_set(data)
                for k, v in rules.items():
                    self.__relate_rule[k] = v

    @property
    def freq_set(self):
        """
        :return: 频繁项集的副本
        """
        return dict(self.__freq_set)
    @property
    def rel_rules(self):
        """
        :return: 关联规则的副本
        """
        return dict(self.__relate_rule)

    def __cal_rel_rule_set(self, data) -> dict:
        """
        获取一个项集中的有效规则
        :param data:单个非空频繁项集 list[items]
        :return:rules dict[tuple(A):set{B}]:A=>B
        """
        rules = {}
        data.sort()

        subsets_data = []
        length = len(data)
        for i in range(1, 2 ** length - 1):  # 子集的个数
            subset = []
            for j in range(length):  # 用来判断二进制数的下标为j的位置的数是否为1
                if (i >> j) % 2:
                    subset.append(data[j])
            subset.sort()
            rest_item = [i for i in data if i not in subset]
            rest_item.sort()

            if self.__freq_set[tuple(data)] / self.__freq_set[tuple(subset)] > self.confidence:
                for num in rest_item:
                    if tuple(subset) in rules.keys():
                        rules[tuple(subset)].add(num)
                    else:
                        rules[tuple(subset)] = {num, }
        return rules

    @staticmethod
    def get_freq_items(item_set: dict, support_num: int) -> dict:
        """
        输出项集中频繁的部分（数据中已经计算好频数）
        :param item_set:dict{tuple:int=freq}
        :param support_num:频繁下界
        :return:dict{tuple:int=freq}
        """
        freq_items = {}
        for key in item_set.keys():
            if item_set[key] >= support_num:
                freq_items[key] = item_set[key]
        return freq_items

    @staticmethod
    def generate_next_level(item_set: dict):
        """
        自然连接
        :param item_set:
        :return:
        """
        res = {}
        datas = []
        for key in item_set.keys():
            datas.append([i for i in key])
        for index in range(len(datas)):
            for index_s in range(index + 1, len(datas)):
                data = list(datas[index])
                for num in datas[index_s]:
                    if not num in data:
                        data.append(num)
                    # print(datas)
                data.sort()
                res[tuple([v for v in data])] = 0
        return res

    @staticmethod
    def count_freq_item(datas: dict, freq_items: dict) -> dict:
        """
        计算项集的频度
        :param datas:
        :param freq_items:dict{tuple:int=0}
        :return: freq_items：dict{tuple:int}
        """
        for record in datas.values():
            for key in freq_items.keys():
                record_haskey = True
                for index in range(len(key)):
                    if not key[index] in record:
                        record_haskey = False
                if record_haskey:
                    freq_items[key] += 1
        # print(freq_items)
        return freq_items

    def cut_tree(self, item_set: dict):
        """
        剪枝 去除子集不频繁的项集
        :param item_set: dict{tuple:int=0}
        :return:
        """
        res = {}
        datas = []
        for key in item_set.keys():
            datas.append([i for i in key])
        # print(datas)
        for item_group in datas:
            if len(item_group) < 2:
                continue
            else:
                is_freq=True
                for index in range(len(item_group)):
                    temp_item_group = list(item_group)
                    temp_item_group.remove(item_group[index])
                    temp_item_group.sort()
                    if not tuple(temp_item_group) in self.__freq_set.keys():
                        is_freq=False
                        break
                if is_freq:
                    res[tuple([v for v in item_group])] = 0
        # print(res)
        return res


if __name__ == '__main__':
    datas = util_m.read_data('../res/data1.json')
    # print(datas)
    test = Apriori(datas=datas, support=0.3, confidence=0.5)
    # test.get_freq_set().clear()
    print(test.freq_set)
    print(util_m.relate_rules2str(test.rel_rules))
