import json
from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.instagram.utils import get_X_IG_App_ID
from SocialMediaScraper.utils import requests_with_retry


class InsPostList:
    def __init__(self, cookies, **kwargs):
        self.headers = HEADERS.copy()
        self.headers.update({'x-csrftoken': cookies['csrftoken'], 'x-ig-app-id': get_X_IG_App_ID(cookies)})
        self.cookies = cookies
        self.proxies = kwargs.get("proxies")
        self.post_list = []

    def get_post_list(self, user_name, post_num, next_max_id=None):
        params = {
            'count': '12',
            'max_id': next_max_id,
        }
        response = requests_with_retry.get(
            f'https://www.instagram.com/api/v1/feed/user/{user_name}/username/',
            params=params, cookies=self.cookies, headers=self.headers, proxies=self.proxies
        )
        try:
            parse_data = json.loads(response.text)
        except:
            raise Exception("IP被ins封禁")
        status = parse_data['status']
        if status != 'ok':
            raise Exception(parse_data['message'])
        else:
            self.post_list.extend([item['code'] for item in parse_data['items']])
            more_available = parse_data.get('more_available')

            if more_available:
                next_max_id = parse_data['next_max_id']
                while more_available and len(self.post_list) < post_num:
                    self.get_post_list(user_name, post_num, next_max_id)
            return [f"https://www.instagram.com/p/{_id}/" for _id in self.post_list[:post_num]]
