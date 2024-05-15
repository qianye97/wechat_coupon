# coding=utf-8
"""
首先要感谢下这篇文章：
https://www.jianshu.com/p/f9b5e3020789

值得看的一篇文章：
http://g.alicdn.com/tmapp/tida-doc/docs/top/00API%E8%B0%83%E7%94%A8%E8%AF%B4%E6%98%8E.html

"""
import hashlib
import json
import random
import time
import urllib
import urllib.parse
import urllib.request

from entity.commodity import Commodity
from entity.coupon import Coupon
from entity.material import Material
from untils.date_util import long_to_timestamp

MATERIAL_SUBJECT = {
    '1': '促销活动',
    '2': '热门主题',
    '3': '精选榜单',
    '4': '行业频道',
    '5': '其他'
}

MATERIAL_TYPE = {
    '1': '商品',
    '2': '权益'
}

COUPON_TYPE = {
    0: '店铺券',
    1: '单品券',
    None: None
}

COUPON_SRC_SCENE = {
    1: '全网公开券',
    4: '妈妈渠道券',
    None: None
}

MAX_COUPON_COUNT = 5
DEFAULT_PAGE_SIZE = '100'
TB_API_ROOT = 'http://gw.api.taobao.com/router/rest?'


class TbApiClient(object):
    def __init__(self, app_key, secret_key, adzone_id):
        self.app_key = app_key
        self.secret_key = secret_key
        self.adzone_id = adzone_id

    #排序
    def ksort(self, d):
        return [(k, d[k]) for k in sorted(d.keys())]

    #MD5加密
    def md5(self, s, raw_output=False):
        """Calculates the md5 hash of a given string"""
        res = hashlib.md5(s.encode())
        if raw_output:
            return res.digest()
        return res.hexdigest()

    #计算sign
    def createSign(self, paramArr):
        sign = self.secret_key
        paramArr = self.ksort(paramArr)
        paramArr = dict(paramArr)
        for k, v in paramArr.items():
            if k != '' and v != '':
                sign += k + v
        sign += self.secret_key
        sign = self.md5(sign).upper()
        return sign

    #参数排序
    def createStrParam(self, paramArr):
        strParam = ''
        for k, v in paramArr.items():
            if k != '' and v != '':
                strParam += k + '=' + urllib.parse.quote_plus(v) + '&'
        return strParam

    def common_query(self, postparm):
        # 公共参数，一般不需要修改
        paramArr = {'app_key': self.app_key,
                    'v': '2.0',
                    'sign_method': 'md5',
                    'format': 'json',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
        paramArr = {**paramArr, **postparm}
        sign = self.createSign(paramArr)
        strParam = self.createStrParam(paramArr)
        strParam += 'sign=' + sign
        url = TB_API_ROOT + strParam
        res = urllib.request.urlopen(url).read()
        return res

    def parse_json(self, json_str):
        json_obj = json.loads(json_str)

        def _parse(json_data):
            nest = False
            for key, value in json_data.items():
                if type(value) == dict or type(value) == list:
                    nest = True
                    break

            for key, value in json_data.items():
                if type(value) == dict:
                    return _parse(value)
                if type(value) == list:
                    return value
                if not nest:
                    return json_data
        return _parse(json_obj)


    def taobao_tbk_dg_optimus_promotion(self, material_id: str):
        '''
        通用物料推荐，传入官方公布的物料id，可获取指定物料
        淘宝接口文档：
        http://bigdata.taobao.com/api.htm?spm=a219a.7386797.0.0.4ad5669aWaaQFi&source=search&docId=33947&docType=2

        :param material_id:  详见https://market.m.taobao.com/app/qn/toutiao-new/index-pc.html#/detail/10628875?_k=gpov9a
        :param adzone_id:  广告位
        :return:
        '''
        # 请求参数，根据API文档修改
        # TODO
        # 把分页现在这里随机有一定考虑
        # 原因是：1. 不同 material_id 得到的数据不一，且刷新周期不一
        #                    2. 微信发送不可太频繁，我仅是怕被封，决定取很小一部分数据
        page_no = str(random.choices(['1','2','3','4', '5', '6', '7', '8', '9'])[0])
        page_size = str(random.randint(8, 10))

        postparm = {
                    'page_no': page_no,
                    'page_size': page_size,
                    'adzone_id': self.adzone_id,
                    'promotion_id': material_id,
                    'method': 'taobao.tbk.dg.optimus.promotion'
                    }

        return self.common_query(postparm)


    def tabao_tbk_commodity_detail(self, item_id, biz_scene_id=1):
        postparm = {
            'item_id': item_id,
            'method': 'taobao.tbk.item.info.upgrade.get',
            'biz_scene_id': str(biz_scene_id)
        }
        return self.parse_json(self.common_query(postparm))


    def tabao_tbk_fetch_materials(self, default_subject=1, default_material_type=1):
        postparm = {
            'material_query': '{"subject": "%s", "material_type": "%s"}' % (default_subject, default_material_type),
            'method': 'taobao.tbk.optimus.tou.material.ids.get'
        }
        res = self.common_query(postparm)
        json_data_list = self.parse_json(res)
        if not json_data_list:
            return []
        materials = []
        for material in json_data_list:
            materials.append(Material(material['material_id'], material['material_name'], material['material_type'],
                     material['subject'], long_to_timestamp(material['start_time']), long_to_timestamp(material['end_time'])))

        return materials

    def package_coupon(self, item_id, coupon_json_data):
        coupon = Coupon(coupon_json_data.get('promotion_id', None), coupon_json_data.get('promotion_desc', None), coupon_json_data.get('promotion_fee', None))
        coupon.coupon_start_time = coupon_json_data.get('promotion_start_time', None)
        coupon.coupon_end_time = coupon_json_data.get('promotion_end_time', None)
        coupon.coupon_title = coupon_json_data.get('promotion_title', None)
        if coupon.coupon_id:
            coupon_info = self.tabao_tbk_coupon_get(item_id, coupon.coupon_id)
            coupon.coupon_type = COUPON_TYPE[coupon_info.get('coupon_type', None)]
            coupon.coupon_src_scene = COUPON_SRC_SCENE[coupon_info.get('coupon_src_scene', None)]
        return coupon

    def extract_coupon(self, commodity, price_promotion_info, keyword1, keyword2):
        final_promotion_path_list = price_promotion_info.get(keyword1, None)
        if final_promotion_path_list:
            final_promotion_path_map_data = final_promotion_path_list.get(keyword2, [])
            for promotion in final_promotion_path_map_data:
                coupon = self.package_coupon(commodity.item_id, promotion)
                if '跨店满减' == coupon.coupon_title:
                    commodity.has_full_reduction = '是'
                    commodity.full_reduction_coupon_set.add(coupon)

                elif coupon.coupon_src_scene == "全网公开券":
                    commodity.has_open_reduction = '是'
                    commodity.open_coupon_set.add(coupon)

                elif coupon.coupon_src_scene == "妈妈渠道券":
                    commodity.has_alimama_reduction = '是'
                    commodity.alimama_coupon_set.add(coupon)

    def package_commodity(self, json_data):
        if type(json_data) != dict:
            return None
        basic_info = json_data.get('item_basic_info', None)
        publish_info = json_data.get('publish_info', None)

        if not basic_info or not publish_info:
            return None
        commodity = Commodity(json_data.get('item_id', None), basic_info.get('short_title', None))
        commodity.annual_vol = basic_info.get('annual_vol', None)
        detail_list = self.tabao_tbk_commodity_detail(commodity.item_id)
        if not detail_list or type(detail_list) != list:
            return None
        detail = detail_list[0]
        price_promotion_info = detail.get('price_promotion_info', None)
        if price_promotion_info:
            commodity.zk_final_price = price_promotion_info.get('zk_final_price', None)
            commodity.reserve_price = price_promotion_info.get('reserve_price', None)
            commodity.final_promotion_price = price_promotion_info.get('final_promotion_price', None)
            commodity.predict_rounding_up_price = price_promotion_info.get('predict_rounding_up_price', None)
            commodity.tb_price = commodity.zk_final_price
            commodity.our_price = commodity.final_promotion_price
            self.extract_coupon(commodity, price_promotion_info, 'final_promotion_path_list', 'final_promotion_path_map_data')
            self.extract_coupon(commodity, price_promotion_info, 'more_promotion_list', 'more_promotion_map_data')
            for coupon in commodity.open_coupon_set:
                if coupon.coupon_fee:
                    commodity.tb_price = float(commodity.tb_price) - float(coupon.coupon_fee)
            for coupon in commodity.full_reduction_coupon_set:
                if coupon.coupon_fee:
                    commodity.tb_price = float(commodity.tb_price) - float(coupon.coupon_fee)

        commodity.title = basic_info.get('title', None)
        commodity.sub_title = basic_info.get('sub_title', None)
        commodity.short_title = basic_info.get('short_title', None)
        commodity.image_url = 'http:' + basic_info.get('pict_url', None)
        commodity.brand_name = basic_info.get('brand_name', None)
        commodity.shop_name = basic_info.get('shop_title', None)
        commodity.tk_total_sales = basic_info.get('tk_total_sales', None)
        click_url = publish_info.get('click_url', '')
        coupon_url = publish_info.get('coupon_share_url', '')
        if not click_url or not coupon_url:
            return None
        commodity.coupon_url = 'http:' + coupon_url
        commodity.click_url = 'http:' + click_url
        return commodity

    def tabao_tbk_material_recommend(self, material_id, page_no=1):
        print(f'获取物料ID：{material_id}, 页码：{page_no}')
        material_id = str(material_id)
        postparm = {
            'page_no': str(page_no),
            'page_size': DEFAULT_PAGE_SIZE,
            'adzone_id': self.adzone_id,
            'material_id': material_id,
            'method': 'taobao.tbk.dg.material.recommend'
        }
        res = self.common_query(postparm)
        json_data_list = self.parse_json(res)
        commodity_list = []
        ending_flag = len(json_data_list) != int(DEFAULT_PAGE_SIZE)
        for json_data in json_data_list:
            commodity = self.package_commodity(json_data)
            if commodity:
                commodity_list.append(commodity)
        return commodity_list, ending_flag

    def tabao_tbk_parse_item_id_by_url(self, url):
        postparm = {
            'item_id': url,
            'method': 'taobao.tbk.item.click.extract'
        }
        return self.common_query(postparm)

    def taobao_tbk_urls_spread(self, urls):
        urls_str = ','.join(['{"url": "%s"}' % url for url in urls])
        postparm = {
            'requests': '[%s]' % urls_str,
            'method': 'taobao.tbk.spread.get'
        }
        json_data_list = self.parse_json(self.common_query(postparm))
        convert_link_list = []
        for json_data in json_data_list:
            convert_link_list.append(json_data.get('content', None))
        return dict(zip(urls, convert_link_list))

    def taobao_tbk_tpwd_create(self, text: str, url: str):
        '''
        提供淘客生成淘口令接口，淘客提交口令内容、logo、url等参数，生成淘口令关键key如：￥SADadW￥，后续进行文案包装组装用于传播
        淘宝接口文档：
        http://bigdata.taobao.com/api.htm?spm=a219a.7386797.0.0.494b669atcwg9a&source=search&docId=31127&docType=2

        :param text: 口令弹框内容
        :param url: 口令跳转目标页
        :return: 返回淘口令，如<￥SADadW￥>
        '''

        postparm = {
                    'text': text,
                    'url': url,
                    'method': 'taobao.tbk.tpwd.create'
                    }
        res = self.common_query(postparm)
        tao_command = json.loads(res)
        if 'tbk_tpwd_create_response' in tao_command:
            return tao_command['tbk_tpwd_create_response']['data']['model']
        return None

    def tkl_parser(self, tkl):
        '''
        :param tkl: str 淘口令，例如 ￥ABCDEFG￥
        :return: str  返回自己的淘口令
        '''
        # 取值地址，接口地址
        url = f'''http://www.taofake.com/index/tools/gettkljm.html?tkl={urllib.parse.quote(tkl)}'''
        # 伪装定义浏览器header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        return self.taobao_tbk_tpwd_create(json.loads(data)['data']['content'], json.loads(data)['data']['url'])

    def taobao_tbk_materials_upgrade(self):
        page_no = '1'
        # page_no = str(random.choices(['1', '2', '3', '4', '5', '6', '7', '8', '9'])[0])
        postparm = {
            'adzone_id': self.adzone_id,
            'page_no': page_no,
            'page_size': DEFAULT_PAGE_SIZE,
            'q': '运动',
            'method': 'taobao.tbk.dg.material.optional.upgrade',
            'has_coupon': 'true'
        }
        json_data_list = self.parse_json(self.common_query(postparm))
        commodity_list = []
        for json_data in json_data_list:
            commodity = self.package_commodity(json_data)
            if commodity:
                commodity_list.append(self.package_commodity(json_data))
        return commodity_list

    def tabao_tbk_coupon_get(self, item_id, promotion_id):
        postparm = {
            'item_id': item_id,
            'activity_id': promotion_id,
            'method': 'taobao.tbk.coupon.get',
        }
        json_data = self.parse_json(self.common_query(postparm))
        return json_data

