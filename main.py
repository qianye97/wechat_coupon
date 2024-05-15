# coding=utf-8
from coupon.tb import fetch_recommend_commodity_list, write_commodity_list
from untils.tb_top_api import TbApiClient

if __name__ == '__main__':
    tb_client = TbApiClient(app_key='34676615', secret_key='797b88452ae19d47d1b2f132f714793b', adzone_id='115690950105')
    write_commodity_list(fetch_recommend_commodity_list(tb_client))
    # run()