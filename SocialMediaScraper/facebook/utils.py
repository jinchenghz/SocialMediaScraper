import json
import re
from SocialMediaScraper.facebook import HEADERS
from SocialMediaScraper.utils import requests_with_retry


def get_fb_dtsg(cookies):
    if isinstance(cookies, str):
        cookies = json.loads(cookies)
    response = requests_with_retry.get('https://www.facebook.com/profile.php?id=100083014643527',
                                       headers=HEADERS, cookies=cookies, timeout=30)
    group = re.findall(r'\{"name":"fb_dtsg","value":"([^"]*?)"\}', response.text)
    if not group:
        group = re.findall(r'"DTSGInitialData":\{"token":"(.*?)"', response.text)
    if not group:
        group = re.findall(r'"DTSGInitialData",\[\],\{"token":"(.*?)"', response.text)
    if group:
        token = group[0]
    else:
        raise Exception('fb_dtsg参数获取失败，可尝试切换cookies重试')
    return token
