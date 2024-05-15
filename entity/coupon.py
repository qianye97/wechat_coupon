from dataclasses import dataclass


@dataclass(repr=True)
class Coupon:
    coupon_id: str
    coupon_desc: str
    coupon_fee: str
    coupon_url: str = None
    coupon_title: str = None
    coupon_start_time: str = None
    coupon_end_time: str = None
    coupon_remain_count: int = None
    coupon_total_count: int = None
    coupon_type: int = None
    coupon_amount: str = None
    coupon_src_scene: str = None

    def __init__(self, coupon_id, coupon_desc, coupon_fee):
        self.coupon_id = coupon_id
        self.coupon_desc = coupon_desc
        self.coupon_fee = coupon_fee

    def __eq__(self, other):
        return self.coupon_id == other.coupon_id

    def __hash__(self):
        return hash(self.coupon_id)
