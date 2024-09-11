import json

from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.instagram.utils import get_X_IG_App_ID
from SocialMediaScraper.models import InsUserItem
from SocialMediaScraper.utils import requests_with_retry


def get_user_data(user_name, cookies, proxies=None):
    headers = HEADERS.copy()
    headers.update({'x-csrftoken': cookies['csrftoken'], 'x-ig-app-id': get_X_IG_App_ID(cookies)})
    params = {
        'username': user_name,
    }
    response = requests_with_retry.get('https://www.instagram.com/api/v1/users/web_profile_info/', params=params,
                                       cookies=cookies, headers=headers, proxies=proxies)
    try:
        # 代理请求错误时，会返回html
        parsed_data = json.loads(response.text)
    except:
        raise Exception("IP被ins封禁")
    status = parsed_data['status']
    if status != 'ok':
        raise Exception(parsed_data['message'])
    else:
        user_info = InsUserItem()
        user = parsed_data['data']['user']
        user_info.avatar = user['profile_pic_url']
        user_info.user_url = f'https://www.instagram.com/{user_name}/'
        user_info.user_name = user['username']
        user_info.screen_name = user['full_name'] if user['full_name'] else user['username']
        user_info.user_id = user['id']
        user_info.followers_count = user['edge_followed_by']['count']
        user_info.post_count = user['edge_owner_to_timeline_media']['count']
        return user_info.__dict__
