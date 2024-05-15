import time
import json
from dataclasses import asdict

import itchat
import random

from tqdm import tqdm

from untils.common import save_pic, del_pic
from untils.csv_util import write_csv
from untils.tb_top_api import TbApiClient, MATERIAL_SUBJECT, MATERIAL_TYPE


def fetch_recommend_commodity_list(tb_client):
    material_id_set = set()
    for material_subject in MATERIAL_SUBJECT.keys():
        for material_type in MATERIAL_TYPE.keys():
            materials = tb_client.tabao_tbk_fetch_materials(material_subject, material_type)
            for material in materials:
                material_id_set.add(material.material_id)

    wait_publish_commodity_list = []
    for material_id in tqdm(material_id_set):
        page_no = 1
        commodity_list, ending_flag = tb_client.tabao_tbk_material_recommend(material_id, page_no)
        while not ending_flag:
            page_no += 1
            next_commodity_list, ending_flag = tb_client.tabao_tbk_material_recommend(material_id, page_no)
        for commodity in commodity_list:
            if not commodity.alimama_coupon_set:
                continue
            if not commodity.click_url:
                continue
            if not commodity.coupon_url:
                continue
            commodity.click_url = tb_client.taobao_tbk_tpwd_create('内部独家', commodity.click_url)
            url_convert_dict = tb_client.taobao_tbk_urls_spread([commodity.coupon_url])
            if commodity.coupon_url not in url_convert_dict:
                continue
            commodity.coupon_url = url_convert_dict[commodity.coupon_url]
            wait_publish_commodity_list.append(commodity)

    return wait_publish_commodity_list


def expand_coupon(commodity, prefix, coupon_set):
    max_cnt = 2
    if not coupon_set:
        return
    for i, coupon in enumerate(coupon_set):
        if i >= max_cnt:
            break
        setattr(commodity, prefix + 'coupon_fee' + str(i), coupon.coupon_fee)
        setattr(commodity, prefix + 'coupon_desc' + str(i), coupon.coupon_desc)
        setattr(commodity, prefix + 'coupon_type' + str(i), coupon.coupon_type)
        setattr(commodity, prefix + 'coupon_src_scene' + str(i), coupon.coupon_src_scene)


def write_commodity_list(commodity_list):
    results = []
    for commodity in commodity_list:
        expand_coupon(commodity, 'open_', commodity.open_coupon_set)
        commodity.open_coupon_set = None

        expand_coupon(commodity, 'alimama_', commodity.alimama_coupon_set)
        commodity.alimama_coupon_set = None

        expand_coupon(commodity, 'full_reduction_', commodity.full_reduction_coupon_set)
        commodity.full_reduction_coupon_set = None

        results.append(asdict(commodity))
    if results:
        write_csv(results[0].keys(), results, '淘宝商品.csv')


def push_commodity_to_wechat(group_name, commodity):
    filename = save_pic(commodity.image_url, commodity.item_id)
    itchat.send('@img@%s' % (f'''{filename}'''), group_name)
    itchat.send(f'''{commodity.click_url}\n【优惠券】{commodity.coupon_url}\n【在售价】¥{commodity.price}【券后价】¥{commodity.final_price}''',
                group_name)
    if filename:
        time.sleep(2)
        del_pic(filename)


def tb_share_text(group_name: str, material_id: str, app_key, app_secret, adzone_id):
    '''

    :param group_name:
    :param material_id:
    :return:
    '''
    tb_client = TbApiClient(app_key=app_key, secret_key=app_secret, adzone_id=adzone_id)

    wait_publish_commodity_list = fetch_recommend_commodity_list(tb_client)[:10]
    try:
        groups = itchat.search_chatrooms(name=f'''{group_name}''')
        for room in groups:
            group_name = room['UserName']
            time.sleep(random.randint(1, 5))
            for commodity in wait_publish_commodity_list:
                push_commodity_to_wechat(group_name, commodity)

    except Exception as e:
        print(e)
        tb_share_text(group_name, material_id, app_key, app_secret, adzone_id)
