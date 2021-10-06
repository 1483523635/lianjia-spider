# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# pc_type           lenovo
# create_date:      2019/2/27
# file_name:        lianjia_crawler.py
# github            https://github.com/inspurer
# qq_mail           2391527690@qq.com

import requests

from concurrent.futures import ThreadPoolExecutor

from pyquery import PyQuery as pq

import json

import threading

import time

import os


def get_list_page_url(url):
    start_url = url
    init_url = start_url.format("")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    try:
        response = requests.get(start_url.format(""), headers=headers)
        # print(response.status_code, response.text)
        doc = pq(response.text)
        total_num = int(doc(".resultDes .total span").text())
        total_page = total_num // 30 + 1
        # 只能访问到前一百页
        if total_page > 100:
            total_page = 100

        page_url_list = list()

        for i in range(total_page):
            page_url_list.append(start_url.format("pg" + str(i + 1)))
            # print(url)
        return page_url_list

    except:
        print("获取总套数出错,请确认起始URL是否正确")
        return None


detail_list = list()


# 需要先在本地开启代理池
# 代理池仓库: https://github.com/Python3WebSpider/ProxyPool
def get_valid_ip():
    url = "http://localhost:5555/random"
    try:
        ip = requests.get(url).text
        return ip
    except:
        print("请先运行代理池")


def get_detail_page_url(page_url):
    global detail_list
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https://bj.lianjia.com/ershoufang'
    }

    try:
        response = requests.get(page_url, headers=headers, timeout=3)
        doc = pq(response.text)
        # broswer.get(page_url)
        # print(page_url)
        # doc = pq(broswer.page_source)
        i = 0
        detail_urls = list()
        for item in doc(".sellListContent li").items():
            i += 1
            if i == 31:
                break
            child_item = item(".noresultRecommend")
            if child_item == None:
                i -= 1
            detail_url = child_item.attr("href")
            detail_urls.append(detail_url)
        return detail_urls
    except:
        print("获取列表页" + page_url + "出错")


lock = threading.Lock()


def send_request(url, with_proxy=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https://bj.lianjia.com/ershoufang'
    }

    if not with_proxy:
        return requests.get(url=url, headers=headers, timeout=3)
    proxies = {
        "http": "http://" + get_valid_ip(),
    }
    return requests.get(url=url, headers=headers, proxies=proxies, timeout=3)


def extract_response(response, detail_url):
    detail_dict = dict()
    doc = pq(response.text)
    unit_price = doc(".unitPriceValue").text()
    unit_price = unit_price[0:unit_price.index("元")]
    title = doc("h1").text()
    area = doc(".areaName .info a").eq(1).text().strip()
    total_price = doc(".total").text()
    xiaoqu_name = doc(".communityName .info").text()
    lou_ceng = doc(".subInfo").eq(0).text()
    zhuang_kuang = doc(".subInfo").eq(1).text()
    fangzi_detail = doc(".subInfo").eq(2).text()
    fang_ling = fangzi_detail[0: fangzi_detail.index("\n")]
    # 塔楼， 板楼
    lou_kuang = fangzi_detail[fangzi_detail.index("\n/")+2:len(fangzi_detail)]

    hu_xing = doc(".mainInfo").eq(0).text()
    chao_xiang = doc(".mainInfo").eq(1).text()
    mian_ji = doc(".mainInfo").eq(2).text()

    url = detail_url
    detail_dict["title"] = title
    detail_dict["area"] = area
    detail_dict["price"] = unit_price
    detail_dict["url"] = url
    detail_dict["total_price"] = total_price
    detail_dict["xiaoqu_name"] = xiaoqu_name
    detail_dict["lou_ceng"] = lou_ceng
    detail_dict["zhuang_kuang"] = zhuang_kuang
    detail_dict["fang_ling"] = fang_ling
    detail_dict["lou_kuang"] = lou_kuang
    detail_dict["hu_xing"] = hu_xing
    detail_dict["chao_xiang"] = chao_xiang
    detail_dict["mian_ji"] = mian_ji

    detail_list.append(detail_dict)
    print(unit_price, title, area, total_price, xiaoqu_name)


def detail_page_parser(res):
    global detail_list
    detail_urls = res.result()
    if not detail_urls:
        print("detail url 为空")
        return None

    for detail_url in detail_urls:
        try:
            response = send_request(detail_url)
            extract_response(response, detail_url)

        except:
            print("获取详情页出错,换ip重试")
            beep()
            try:
                response = send_request(detail_url, True)
                extract_response(response, detail_url)
            except:
                beep()
                time.sleep(20)


def beep():
    os.system('say "error happened."')


def save_data(data, filename):
    with open(filename + ".json", 'w', encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


def load_data_from_file():
    with open("url.json", "r", encoding="utf-8") as f:
        str = f.read()
        data = json.loads(str)
    return data


def main():
    # cq,cs,nj,dl,wh,cc
    urls = load_data_from_file()
    for index, url in enumerate(urls):
        page_url_list = get_list_page_url(url)
        print(page_url_list)
        # pool = threadpool.ThreadPool(20)
        # requests = threadpool.makeRequests(page_and_detail_parser, page_url_list)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()

        p = ThreadPoolExecutor(30)

        for page_url in page_url_list:
            p.submit(get_detail_page_url, page_url).add_done_callback(detail_page_parser)
        # 这里的回调函数拿到的是一个对象。
        # 先把返回的res得到一个结果。即在前面加上一个res.result(),这个结果就是get_detail_page_url的返回
        p.shutdown()

        print(detail_list)

    save_data(detail_list, "chaoyang-tianshuiyuan-1-2-ju-banlou")

    detail_list.clear()


if __name__ == '__main__':
    old = time.time()
    main()
    new = time.time()
    delta_time = new - old
    print("程序共运行{}s".format(delta_time))
