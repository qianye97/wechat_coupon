from datetime import datetime


def long_to_timestamp(timestamp):
    if len(str(timestamp)) == 13:
        timestamp /= 1000
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp)

    # 将datetime对象转换为字符串，指定格式
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date  # 输出类似：2021-01-01 00:00:00

