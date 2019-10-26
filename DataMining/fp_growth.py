1  # !/usr/bin/env python
2  # -*- coding: utf-8 -*-
3  # @Time  : 11:25
4  # @File  : fp_growth.py
5  # @Author: Ch
6  # @Date  : 2019/10/23
import json
import util_m as util


class FpPoint:

    def __init__(self, tag, pa, count=1):
        self.__item_tag = tag
        self.__parent = pa
        self.__freq_count = count
        self.children = []

    def add_count(self, count=1):
        self.__freq_count += count

    @property
    def count(self):
        return self.__freq_count

    @property
    def parent(self):
        return self.__parent

    @property
    def item_tag(self):
        return self.__item_tag

    def add_child(self, tag, count=1):
        child = FpPoint(tag, self, count=count)
        self.children.append(child)
        return child

    def set_parent(self, parent):
        self.__parent = parent

    def set_count(self, count):
        self.__freq_count = count

    def tuple_s(self):
        """
        tag，count 字符串
        :return:
        """
        return str("%d,%d" % (self.item_tag, self.count))

    def get_sign_s(self):

        if len(self.children) > 0:
            dict = {self.tuple_s(): []}
            for child in self.children:
                dict[self.tuple_s()].append(child.get_sign_s())
            return dict
        else:
            return self.tuple_s()

    def tuple(self):
        return tuple([self.item_tag, self.count])

    def print(self, indent=0):
        print(" " * indent, '|-', self.tuple())
        for child in self.children:
            child.print(indent + 6)


class FPGrowth:
    @property
    def freq_set(self):
        """
        频繁项集
        :return:
        """
        return dict(self.__freq_set)
    @property
    def relate_rule(self):
        """
        关联关系
        :return:
        """
        return dict(self.__relate_rule)

    def __init__(self, datas: dict, support, confidence):
        """
        类构造函数
        :param datas:数据集{记录名：项目集}
        :param support: 最小支持度
        :param confidence: 最小置信度
        """
        self.__fp_chain = {}  # 项关联的全部树节点{tag:[list of point]}
        self.__freq_set = {}  # 结果1 频繁项集
        self.__relate_rule = {}  # 结果2 关联规则
        self.fp_tree_root_point = None  # 频繁树的根节点
        self.support_num = int(support * len(datas.keys()))  # 满足最小支持度的频数
        self.confidence = confidence  # 置信度
        self.__item_set = self.get_item_set(datas, self.support_num)  # 有序标签项目集
        print(self.__item_set)
        # fp树构建
        self.fp_tree_root_point = self.build_fp_tree(datas, self.__item_set)
        # 打印fp-tree
        # self.fp_tree_root_point.print()

        # 构建项目关联链
        self.__fp_chain = self.get_chain(self.fp_tree_root_point)
        # print(self.__fp_chain)
        # 挖掘频繁项集
        for key_of_set in self.__fp_chain.keys():
            # terminal_point = [i for i in self.__fp_chain[key_of_set] if (i.children) == 0]
            temp_freq_set = self.dig4item(self.__fp_chain[key_of_set], (key_of_set,),
                                          self.__item_set[0:self.__item_set.index(key_of_set)], self.support_num)
            for k, v in temp_freq_set.items():
                self.__freq_set[k] = v
        #  完成频繁项集查找 接下来获取关联规则
        # init relate_rules
        for item_group in self.__freq_set.keys():
            if len(item_group) == 1:
                continue
            else:
                data = [i for i in item_group]  # 一个频繁项集
                rules = self.__cal_rel_rule_set(data)
                for k, v in rules.items():
                    self.__relate_rule[k] = v
        return

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
    def get_item_set(datas, support_num):
        """
        获取所有频繁项目
        :param datas:
        :param support_num:
        :return: 排序的tag数组 频数从高到低
        """
        item_set = {}
        for record in datas.values():
            for item in record:
                if item in item_set.keys():
                    item_set[item] += 1
                else:
                    item_set[item] = 1
        # 去除非频繁项转为元组数组[(key,value),]
        item_set = sorted([i for i in item_set.keys() if item_set[i] >= support_num], key=lambda x: item_set[x],
                          reverse=True)
        return item_set

    @staticmethod
    def build_fp_tree(data_raw: dict, item_set):
        """
        从原始数据构建频繁模式树
        :param data_raw:
        :param item_set: [tuple(tag,count)]
        :return: 根节点
        """
        root_point = FpPoint(tag=None, pa=None, count=0)
        # print(item_set)   # [(2, 8), (1, 7), (3, 6), (5, 2), (4, 2)]
        # 构建 fp tree
        for record in data_raw.values():
            pointer = root_point
            for item in item_set:
                if item in record:
                    target = None
                    for child in pointer.children:
                        if child.item_tag == item:
                            target = child
                    if not target is None:
                        target.add_count()
                    else:
                        target = pointer.add_child(item)
                    pointer = target
        return root_point

    @staticmethod
    def get_chain(root_point):
        """
        获取项目关联链
        :param root_point:
        :return: dict{tag:[fp_point]}
        """
        chain = {}
        for child in root_point.children:
            FPGrowth.add2chain(child, chain)
        return chain

    @staticmethod
    def add2chain(pointer, chain):
        """
        将Point添加到项目关联链
        :param pointer:
        :param chain:
        :return:
        """
        if pointer.item_tag in chain.keys():
            chain[pointer.item_tag].append(pointer)
        else:
            chain[pointer.item_tag] = [pointer]
        for child in pointer.children:
            FPGrowth.add2chain(child, chain)
        return

    @staticmethod
    def dig4item(item_points, item_tag: tuple, rest_items: list, support_num: int):
        """
        对特定tag在item_points所在的树进行挖掘
        :param item_points: fp_groeth tag=item_tag
        :param item_tag:
        :param rest_items:
        :return:
        """
        freq_set = {}
        if 0 == len(item_points):
            return freq_set
        else:
            # 查找当前树的根节点
            root_point = item_points[0]
            while not root_point.parent is None:
                root_point = root_point.parent
            # 检测自身频繁性
            freq_count = 0
            for item_point in item_points:
                freq_count += item_point.count
            # print(item_tag, freq_count)
            if freq_count >= support_num:
                freq_set[item_tag] = freq_count
                # 查找条件模式基
                fp_base = []
                for item_point in item_points:
                    base_of_item_point = {}  # 一项频繁模式基
                    min_count = item_point.count
                    while item_point.parent.parent is not None:
                        item_point = item_point.parent
                        # if item_point.count > min_count:
                        base_of_item_point[item_point.item_tag] = min_count
                    fp_base.append(base_of_item_point)
                # 条件模式基构造完成
                # print("fp_base:", item_tag, fp_base)
                # 构造条件模式树
                root_point_cp_tr = FPGrowth.build_tree_fp_base(fp_base, rest_items)
                # root_point_cp_tr.print()
                # 构造项目关联链
                fp_chain = FPGrowth.get_chain(root_point_cp_tr)
                # 递归
                for item in fp_chain.keys():
                    tag_temp = list(item_tag)
                    tag_temp.append(item)
                    tag_temp.sort()
                    temp_freq_set = FPGrowth.dig4item(fp_chain[item], tuple(tag_temp),
                                                      rest_items[0: rest_items.index(item)],
                                                      support_num)
                    for k, v in temp_freq_set.items():
                        freq_set[k] = v
            # print("freq-set",freq_set)
            return freq_set

    @staticmethod
    def build_tree_fp_base(fp_base: list, item_list):
        """
        从获取的条件模式基构建频繁模式树
        :param fp_base:[{tag:count}]
        :param item_list:[item]
        :return:根节点
        """
        root_point = FpPoint(tag=None, pa=None, count=0)
        # print(item_set)
        # 构建 条件fp tree
        for record in fp_base:
            pointer = root_point
            for item in item_list:
                if item in record.keys():
                    target = None
                    for child in pointer.children:
                        if child.item_tag == item:
                            target = child
                    if not target is None:
                        target.add_count(record[item])
                    else:
                        target = pointer.add_child(item, record[item])

                    pointer = target
        # root_point.print()
        return root_point

    @staticmethod
    def dict_and_dict(dict1: dict, dict2: dict):
        for k, v in dict2.items():
            if k in dict1.keys():
                dict1[k] += dict2[k]
            else:
                dict1[k] = dict2[k]
        return dict1


if __name__ == '__main__':
    data = util.read_data('../res/data1.json')
    # print(data)
    test = FPGrowth(data, 0.2, 0.5)
    test.fp_tree_root_point.print()
    print(test.freq_set)
    print(util.relate_rules2str(test.relate_rule))
