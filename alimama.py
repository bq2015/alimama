# coding:utf-8
import json
import time

import requests
from selenium import webdriver
from datetime import datetime, timedelta
import json
import argparse


class Spider(object):
    """ alimama main spider """

    def __init__(self):

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        self.web = webdriver.Chrome(chrome_options=chrome_options, )
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
            # user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            #'user-agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            'user-agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)'
        }
        self.req = requests.Session()
        self.cookies = {}

    def login(self, username, password):
        """ login """
        self.web.get(
            'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=false&css_style=alimama&from=alimama&redirectURL=http%3A%2F%2Fwww.alimama.com&full_redirect=true')
        # self.web.find_element_by_class_name('login-switch').click()
        time.sleep(3)
        print(f'login with {username} {password}')
        self.web.find_element_by_id('TPL_username_1').send_keys(username)
        self.web.find_element_by_id('TPL_password_1').send_keys(password)
        time.sleep(2)
        self.web.find_element_by_id('J_SubmitStatic').click()
        # 等待5秒
        self.web.get('http://pub.alimama.com/myunion.htm')
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()

    def refresh(self, url):
        """refersh """
        self.web.get(url)
        time.sleep(3)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies

        content = self.web.page_source
        return content

    def get_taoke_order_list(self):
        t = int(time.time() * 1000)
        now = datetime.now()
        start_date = (now + timedelta(days=-30)) .strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")

        url = f'http://pub.alimama.com/report/getTbkPaymentDetails.json?startTime={start_date}&endTime={end_date}&payStatus=&queryType=1&toPage=1&perPageSize=50&total=&t={t}&pvid=&_tb_token_={self.token}&_input_charset=utf-8'
        web_data = self.req.get(url, headers=self.headers)

        data = json.loads(web_data.text)
        print(data['data']['paymentList'])

    # 创建推广位
    def add_ad(self):
        name = input()
        res = self.req.post('http://pub.alimama.com/common/adzone/selfAdzoneCreate.json', data={
            'tag': '29',
            'gcid': '8',
            'siteid': 'xxxxxxxx',  # 这里改成导购位ID
            'selectact': 'add',
            'newadzonename': name,
            '_tb_token_': self.token
        }, headers=self.headers)

        print(res.text)

    def get_list_keywords(self, channel, page_size=50):
        """ get product list by keywords """
        t = int(time.time() * 1000)
        url = f'https://pub.alimama.com/items/channel/{channel}.json?channel={channel}&perPageSize={page_size}&shopTag=&t={t}&_tb_token_={self.token}&pvid='
        res = self.req.get(url, headers=self.headers)
        rj = res.json()
        print(f' get_list_keywords  {channel} {rj["ok"]}  {len(rj["data"]["pageList"])}')
        if len(rj['data']['pageList']) > 0:
            return rj['data']['pageList']
        else:
            return 'no match item'

    def get_host_product(self, orimemberId, shop_name):
        """ get hot product by orimemberid """
        t = int(time.time() * 1000)
        url = f'https://pub.alimama.com/shopdetail/hotProducts.json?sortField=_totalnum&oriMemberId={orimemberId}&t={t}&pvid=&_tb_token_={self.token}&_input_charset=utf-8'
        content = self.refresh(url)
        content = content[121:-20]
        rj = json.loads(content)
        print(f' get_host_product  {shop_name}: {orimemberId}  {rj["ok"]}  {len(rj["data"]["pagelist"])} \n {url}')
        if len(rj['data']['pagelist']) > 0:
            return rj['data']['pagelist']
        else:
            return 'no match item'

    # https://pub.alimama.com/shopsearch/shopList.json?spm=a2320.7388781.a214tr8.d006.12b82560OMX8yq&q=sdf&toPage=1&perPagesize=40&t=1514189329858&pvid=51_218.17.158.52_3072_1514189325299&_tb_token_=33931586e65ea&_input_charset=utf-8

    # {
        # 			'address' : None,
        # 			'status' : None,
        # 			'memberID' : 13498885,
        # 			'oriMemberId' : 263817957,
        # 			'shopType' : 2,
        # 			'userTag' : 0,
        # 			'shopTitle' : '韩都衣舍旗舰店',
        # 			'pictUrl' : '//img.alicdn.com/shop-logo/63/a7/TB1cOF2JXXXXXbfaXXXSutbFXXX.jpg',
        # 			'coupon' : '0',
        # 			'minCommissionRate' : None,
        # 			'maxCommissionRate' : None,
        # 			'updateTime' : None,
        # 			'extNick' : '韩都衣舍旗舰店',
        # 			'sellerSum' : 0,
        # 			'promotedType' : None,
        # 			'starts' : None,
        # 			'shopUrl' : 'http : //shop58501945.taobao.com/',
        # 			'shopCommissionRate' : 912,
        # 			'cpashop' : '0',
        # 			'shopKeeperCardURL' : None,
        # 			'epcUpdateTime' : None,
        # 			'exLevel' : None,
        # 			'sortRank' : None,
        # 			'exSysType' : None,
        # 			'isJoinedCps' : None,
        # 			'shopCatID' : 14,
        # 			'shopCatName' : '女装/流行女装',
        # 			'shopEpc' : None,
        # 			'shopAuctionCount' : 2546,
        # 			'totalAction' : 324198,
        # 			'rankIcon' : '&lt;imgsrc="//img.alicdn.com/newrank/s_crown_5.gif"/&gt;',
        # 			'rptCpsSh30dDTO' : None,
        # 			'bonusCouponDTO' : None,
        # 			'sellerEventDTO' : None,
        # 			'bonus' : '0',
        # 			'sellerevent' : '0'
        # 		},
    def get_list_shops(self, keywords, page_size=10):
        """ get product list by keywords """
        t = int(time.time() * 1000)
        url = f'https://pub.alimama.com/shopsearch/shopList.json?q={keywords}&toPage=1&perPagesize={page_size}&t={t}&pvid=&_tb_token_={self.token}&_input_charset=utf-8'
        content = self.refresh(url)
        content = content[121:-20]
        rj = json.loads(content)
        print(f' get_list_shops  {keywords} {rj["ok"]}  {len(rj["data"]["pagelist"])}')
        if len(rj['data']['pagelist']) > 0:
            return rj['data']['pagelist']
        else:
            return 'no match item'

    def get_tk_link(self, auctionid):
        """get taobaoke  link"""
        t = int(time.time() * 1000)
        pvid = ''
        gcid, siteid, adzoneid = self.__get_tk_link_s1(auctionid, pvid)
        self.__get_tk_link_s2(gcid, siteid, adzoneid, auctionid, pvid)
        res = self.__get_tk_link_s3(auctionid, adzoneid, siteid, pvid)
        return res

    # 第一步，获取推广位相关信息
    def __get_tk_link_s1(self, auctionid, pvid):
        t = int(time.time() * 1000)
        url = f'http://pub.alimama.com/common/adzone/newSelfAdzone2.json?tag=29&itemId={auctionid}&blockId=&t={t}&_tb_token_={self.token}&pvid={pvid}'
        content = self.refresh(url)
        content = content[121:-20]
        print(content[:100])
        rj = json.loads(content)
        gcid = rj['data']['otherList'][0]['gcid']
        siteid = rj['data']['otherList'][0]['siteid']
        adzones = rj['data']['otherAdzones']
        adzone_ids = [adzone['sub'][0]['id']
                      for adzone in adzones if 'sub' in adzone]
        print(adzone_ids)
        adzoneid = adzone_ids[0]
        return gcid, siteid, adzoneid

    # post数据headers
    def __get_tk_link_s2(self, gcid, siteid, adzoneid, auctionid, pvid):
        url = 'http://pub.alimama.com/common/adzone/selfAdzoneCreate.json'
        data = {
            'tag': '29',
            'gcid': gcid,
            'siteid': siteid,
            'selectact': 'sel',
            'adzoneid': adzoneid,
            't': int(time.time() * 1000),
            '_tb_token_': self.token,
            'pvid': pvid,
        }
        headers = self.headers
        headers = headers.update({
            'Content-Length': str(len(json.dumps(data))),
            'Origin': 'http://pub.alimama.com',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
        })
        res = self.req.post(url, headers=headers, data=data)
        return res

    # 获取口令
    def __get_tk_link_s3(self, auctionid, adzoneid, siteid, pvid):

        t = int(time.time() * 1000)
        url = f'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid={auctionid}&adzoneid={adzoneid}&siteid={siteid}&scenes=1&t={t}&_tb_token_={self.token}&pvid='
        headers = self.headers
        print(f'get_tk_link_s3   {url}')
        content = self.refresh(url)
        content = content[121:-20]
        print(content[:100])
        rj = json.loads(content)

        return rj['data']

    # 获取推广位列表
    def get_ad_list(self):
        res = self.req.get(
            'http://pub.alimama.com/common/adzone/adzoneManage.json?tab=3&toPage=1&perPageSize=40&gcid=8',
            headers=self.headers)
        print(res.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Alimama Spider Tools -u <username> -p <password> ")
    parser.add_argument("username", type=str, help="Taobao UserName")
    parser.add_argument("password", type=str, help="Taobao password")
    args = parser.parse_args()
    assert args.username, "miss Arguments Taobao UserName ? "
    assert args.password, "miss Arguments Taobao Password ? "

    sp = Spider()
    sp.login(username=args.username, password=args.password)
    ###
    # product_keywords = 'muying'

    # print(f'using shop keywords {product_keywords}')
    # product_lists = sp.get_list_keywords(product_keywords, page_size=20)
    # product_lists = product_lists[:3]
    # print(len(product_lists))

    # for i, product in enumerate(product_lists):
    #     print('=' * 20, i)

    #     tk_result = sp.get_tk_link(product['auctionId'])
    #     print(tk_result)
    #     print('=' * 20)

    ###

    shop_keywords = '韩都衣舍'
    print(f'using shop keywords {shop_keywords}')

    shop_list = sp.get_list_shops(shop_keywords,  page_size=10)
    shop_first = shop_list[0]

    orimemberId = shop_first['oriMemberId']
    shop_name = shop_first['extNick']
    shop_url = shop_first['shopUrl']

    product_lists = sp.get_host_product(
        orimemberId, shop_name + ' ' + shop_url)
    product_lists = product_lists[:3]

    for i, product in enumerate(product_lists):
        print('=' * 20, i)
        tk_result = sp.get_tk_link(product['auctionId'])
        print(tk_result)
        print('=' * 20)

    sp.web.quit()
