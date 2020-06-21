#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/6/16 
# @Author : ytq
# @File : test_api.py
# @Software: PyCharm

import jsonpath
import pytest
import requests
import yaml


class TestDemo:
    '''
    定义url的地址
    '''
    __login_url = "http://106.53.223.46:9091/api/v1/user/login"
    __list_url = "http://106.53.223.46:9091/api/v1/menu/list"
    __logout_url = "http://106.53.223.46:9091/api/v1/user/logout"
    __confirm_url = "http://106.53.223.46:9091/api/v1/menu/confirm"

    def login(self, username="user01", password="pwd"):
        '''
        实现login，并且默认user01登录，给其他接口使用
        :param username: 登录的用户名
        :param password: 登录的密码
        :return:返回login的response信息
        '''
        data = {
            "authRequest": {
                "userName": username,
                "password": password
            }
        }
        return requests.post(self.__login_url, json=data).json()

    def get_headers(self):
        '''
        使用默认用户登录，拼接依赖登录接口需要的默认headers
        :return: 默认headers
        '''
        access_token = self.login()["access_token"]
        return {
            'access_token': access_token
        }

    @pytest.mark.parametrize("username, password,rst",
                             [("user01", "pwd", "200"), ("user10", "pwd1", "401"), ("user20", "pwd", "401")])
    def test_login(self, username, password, rst):
        '''
        登录的测试方法，测试成功登录，错误密码登录，错误用户名登录
        :param username: 用户名
        :param password: 密码
        :param rst: 期望返回值
        :return: None
        '''
        ret = self.login(username, password)
        assert ret["code"] == rst

    @pytest.mark.parametrize("username, password,rst",
                             [("user01", "pwd", "200"), ("user10", "pwd1", "401"), ("user20", "pwd", "401")])
    def test_logout(self, username, password, rst):
        '''
        登出的测试方法，测试登录成功的用户登出及登录失败用户的登出，
        因为登录失败无法获取到token，故登录失败的token置为空
        :param username: 用户名
        :param password: 密码
        :param rst: 期望返回值
        :return: None
        '''
        login_ret = self.login(username, password)
        if login_ret["code"] == "200":
            access_token = login_ret["access_token"]
        else:
            access_token = None
        headers = {"access_token": access_token}
        ret = requests.delete(self.__logout_url, headers=headers).json()
        assert ret["code"] == rst

    def test_get_list(self):
        '''
        菜单获取接口测试，默认用户登录后获取到菜单后进行菜单列表长度的判断，以及简单的内容判断，
        用到了多重断言pytest-assume
        :return:None
        '''
        heard = self.get_headers()
        ret = requests.get(self.__list_url, headers=heard).json()
        menu_name = jsonpath.jsonpath(ret, "$..menu_name")
        pytest.assume(len(menu_name) == 18)
        pytest.assume("烧饼" in menu_name)

    @pytest.mark.parametrize("oder_list,rst", yaml.safe_load(open("order.yaml")))
    def test_confirm(self, oder_list, rst):
        '''
        下单接口测试，从yaml中读取数据进行参数化测试；入参中包括点餐的编号和点的数量
        返回的参数为点单的菜品的总数和菜品的总价格，用到了多重断言pytest-assume
        :param oder_list:点餐接口所需的点餐请求列表
        :param rst:预期的菜品总数量和总价格
        :return:None
        '''
        heard = self.get_headers()
        data = oder_list
        ret = requests.post(self.__confirm_url, headers=heard, json=data).json()
        pytest.assume(rst["total"] == ret["total"])
        pytest.assume(rst["total_price"] == ret["total_price"])
