from dataclasses import dataclass

from entity.coupon import Coupon


@dataclass(repr=True)
class Commodity:
    item_id: str
    name: str
    brand_name: str = None
    tb_price: str = None
    our_price: str = None
    zk_final_price: str = None
    reserve_price: str = None
    final_promotion_price: str = None
    predict_rounding_up_price: str = None
    shop_name: str = None
    title: str = None
    sub_title: str = None
    short_title: str = None
    image_url: str = None
    click_url: str = None
    annual_vol: str = None
    tk_total_sales: str = None
    coupon_url: str = None
    has_full_reduction: str = '否'
    full_reduction_coupon_set: set = None
    full_reduction_coupon_fee0: str = None
    full_reduction_coupon_desc0: str = None
    full_reduction_coupon_type0: str = None
    full_reduction_coupon_src_scene0: str = None
    full_reduction_coupon_fee1: str = None
    full_reduction_coupon_desc1: str = None
    full_reduction_coupon_type1: str = None
    full_reduction_coupon_src_scene1: str = None
    has_alimama_reduction: str = '否'
    alimama_coupon_set: set = None
    alimama_coupon_fee0: str = None
    alimama_coupon_desc0: str = None
    alimama_coupon_type0: str = None
    alimama_coupon_src_scene0: str = None
    alimama_coupon_fee1: str = None
    alimama_coupon_desc1: str = None
    alimama_coupon_type1: str = None
    alimama_coupon_src_scene1: str = None
    has_open_reduction: str = '否'
    open_coupon_set: set = None
    open_coupon_fee0: str = None
    open_coupon_desc0: str = None
    open_coupon_type0: str = None
    open_coupon_src_scene0: str = None
    open_coupon_fee1: str = None
    open_coupon_desc1: str = None
    open_coupon_type1: str = None
    open_coupon_src_scene1: str = None

    def __init__(self, item_id, name):
        self.item_id = item_id
        self.name = name
        self.full_reduction_coupon_set = set()
        self.alimama_coupon_set = set()
        self.open_coupon_set = set()

    def get_scene(self):
        return "1" if len(self.item_id) == 50 else "2"
