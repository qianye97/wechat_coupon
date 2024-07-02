# coding=utf-8
import os
from concurrent.futures import ThreadPoolExecutor

from coupon.tb import fetch_recommend_commodity_list, write_commodity_list, RESOURCE_DIR
from untils.tb_top_api import TbApiClient
from flask import Flask, jsonify, request, send_file
app = Flask(__name__)


executor = ThreadPoolExecutor(2)

@app.route("/startFetch")
def start_fetch():
    app_key = request.args.get('app_key')
    if not app_key:
        app_key = '34676615'
    secret_key = request.args.get('secret_key')
    if not secret_key:
        secret_key = '797b88452ae19d47d1b2f132f714793b'
    adzone_id = request.args.get('adzone_id')
    if not adzone_id:
        adzone_id = '115690950105'
    material_id_set = set()
    material_id = request.args.get('material_id')
    if material_id:
        material_id_set = set(material_id.split(','))
    tb_client = TbApiClient(app_key=app_key, secret_key=secret_key, adzone_id=adzone_id)
    executor.submit(fetch_recommend_commodity_list, tb_client, material_id_set)
    return jsonify({"code": 200, "msg": "开始获取成功！", 'result': ""})


@app.route("/getFile")
def get_file():
    return send_file(RESOURCE_DIR + '淘宝商品.csv', as_attachment=True)


@app.route("/removeFile")
def remove_file():
    os.remove(RESOURCE_DIR + '淘宝商品.csv')
    return jsonify({"code": 200, "msg": "文件删除成功！", 'result': ""})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

# if __name__ == '__main__':
#     tb_client = TbApiClient(app_key='34676615', secret_key='797b88452ae19d47d1b2f132f714793b', adzone_id='115690950105')
#     fetch_recommend_commodity_list(tb_client)