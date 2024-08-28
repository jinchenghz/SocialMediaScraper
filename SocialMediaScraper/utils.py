import json
import math
import re
import uuid
from socket import socket
from hashlib import md5
import requests
import socks
from tenacity import retry, stop_after_attempt, wait_fixed
from SocialMediaScraper.facebook import HEADERS
from SocialMediaScraper.logging_config import LoggerUtil

logger = LoggerUtil().get_logger()


def get_md5(content):
    m = md5()
    m.update(content.encode())
    result = m.hexdigest()
    return result


def logging_cache_response(response, requestId):
    _response = str(response)
    _length = len(_response)
    _times = math.ceil(_length / 4000)
    _times = _times if _times < 20 else 20
    for i in range(_times):
        logger.info(f"- {requestId} - Return response ** PART {i + 1} **: {_response[i * 4000:(i + 1) * 4000]}")
    return response


def get_fb_dtsg(cookies, ):
    if isinstance(cookies, str):
        cookies = json.loads(cookies)
    response = requests_with_retry.get('https://www.facebook.com/profile.php?id=100083014643527',
                                       headers=HEADERS, cookies=cookies, timeout=30)
    # print(response)
    group = re.findall(r'\{"name":"fb_dtsg","value":"([^"]*?)"\}', response.text)
    if not group:
        group = re.findall(r'"DTSGInitialData":\{"token":"(.*?)"', response.text)
    if not group:
        group = re.findall(r'"DTSGInitialData",\[\],\{"token":"(.*?)"', response.text)
    logger.info(f" - get_fb_dtsg - {group}")
    if group:
        token = group[0]
    else:
        raise Exception('fb_dtsg参数获取失败，可尝试切换cookies重试')
    return token


class requests_with_retry:
    def __init__(self):
        socket.socket = socks.socksocket

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get(url, params=None, headers=None, cookies=None, proxies=None, timeout=30, json=None):
        # try:
        response = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies, timeout=timeout,
                                json=json)
        return response

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def post(url, params=None, data=None, headers=None, cookies=None, proxies=None, timeout=30, json=None):
        response = requests.post(url, params=params, data=data, headers=headers, cookies=cookies, proxies=proxies,
                                 timeout=timeout, json=json)
        return response


def get_uuid():
    return str(uuid.uuid1()).replace('-', '')
