# -*- coding: utf-8 -*-

class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie

    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie.split(';')
        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict

if __name__ == "__main__":
    cookie = "cye=hangzhou; _lxsdk_cuid=162c4b71d7bc8-086328a63b9d37-444a012d-144000-162c4b71d7cc8;" \
             " _lxsdk=162c4b71d7bc8-086328a63b9d37-444a012d-144000-162c4b71d7cc8; " \
             "_hc.v=c811dce0-8f8a-1198-f711-de68d0ea4a4a.1523718758; s_ViewType=10;" \
             " __utmz=1.1523719760.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none);" \
             " aburl=1; dper=6691f6f2f3756ca897b8ab0f57e626d756ccfb0dcb2a98c83f8ff269c03f2ed5;" \
             " ua=dpuser_7996156562; ctu=90c56af5d389abd5ca65f22e1b762495cb609fffa82314e4dcc02c4e6f6d8635;" \
             " ll=7fd06e815b796be3df069dec7836c3df; cy=3; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic;" \
             " __utma=1.329603921.1523719760.1523719760.1523949947.2; __utmc=1; __utmb=1.1.10.1523949947;" \
             " _lxsdk_s=162d25cfaf0-6d7-ece-2e7%7C%7C140"
    trans = transCookie(cookie)
    print (trans.stringToDict())