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
"""

[
    {
        "domain": ".instagram.com",
        "expirationDate": 1759370928.042556,
        "hostOnly": false,
        "httpOnly": true,
        "name": "datr",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "robOZiBaoXWOhBy6MjGZJXYf"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1756346713.878806,
        "hostOnly": false,
        "httpOnly": false,
        "name": "ig_nrcb",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1732589639.016978,
        "hostOnly": false,
        "httpOnly": false,
        "name": "ds_user_id",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "68664077427"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1756263239.016844,
        "hostOnly": false,
        "httpOnly": false,
        "name": "csrftoken",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "jgx2IMZbeCxnhL8M8WCl0UXX0idTnL8w"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1756346714.682209,
        "hostOnly": false,
        "httpOnly": true,
        "name": "ig_did",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "BD1BD47A-1816-47DC-BB2D-98433C95DCC4"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1725418426,
        "hostOnly": false,
        "httpOnly": false,
        "name": "wd",
        "path": "/",
        "sameSite": "lax",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1707x833"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1759370713.878771,
        "hostOnly": false,
        "httpOnly": false,
        "name": "mid",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "Zs6F2QALAAFtPTk4ZMM0Imu8htbN"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1756349614.585041,
        "hostOnly": false,
        "httpOnly": true,
        "name": "sessionid",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "68664077427%3ABIhuDMrTMEjYBt%3A18%3AAYfIPYgzsG0jLb7IABBtnX8E96TkpXMGGeRjh1dAuw"
    },
    {
        "domain": ".instagram.com",
        "expirationDate": 1725418426,
        "hostOnly": false,
        "httpOnly": false,
        "name": "dpr",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1.5"
    },
    {
        "domain": ".instagram.com",
        "hostOnly": false,
        "httpOnly": true,
        "name": "rur",
        "path": "/",
        "sameSite": "lax",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "\"EAG\\05468664077427\\0541756349638:01f79699f4830dea88e37b15d0fe3d754beaf303ed3780005ea8688e2a0590ecb9a3b8e7\""
    }
]
"""