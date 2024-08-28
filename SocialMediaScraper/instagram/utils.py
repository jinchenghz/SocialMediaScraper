import re
from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.utils import requests_with_retry


def get_fb_dtsg(code, cookie):
    response = requests_with_retry.get(f'https://www.instagram.com/p/{code}/', cookies=cookie, headers=HEADERS)
    token = None
    group = re.search(r'"DTSGInitialData":{"token":"(.*?)"', response.text)
    if group is not None:
        token = re.search(r'"DTSGInitialData":{"token":"(.*?)"', response.text).group(1)
    if token is None or token == '':
        group = re.search(r'"DTSGInitialData",\[],{"token":"(.*?)"', response.text)
        if group is not None:
            token = re.search(r'"DTSGInitialData",\[],{"token":"(.*?)"', response.text).group(1)
    return token


def get_X_IG_App_ID(cookie):
    response = requests_with_retry.get('https://www.instagram.com/lamlamjessie/', cookies=cookie, headers=HEADERS)
    match = re.search(r'"customHeaders":\{"X-IG-App-ID":"(\d+)"', response.text)
    if match:
        profile_owner_id = match.group(1)
        return profile_owner_id
    else:
        raise Exception("X-IG-App-ID参数获取失败，请更换cookies")
