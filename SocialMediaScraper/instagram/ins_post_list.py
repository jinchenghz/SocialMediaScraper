import json
from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.instagram.utils import get_X_IG_App_ID
from SocialMediaScraper.models import InsPostListItem
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
        # print(response.text)
        try:
            parse_data = json.loads(response.text)
        except:
            raise Exception("IP被ins封禁")
        status = parse_data['status']
        if status != 'ok':
            raise Exception(parse_data['message'])
        for post in parse_data['items']:
            item = InsPostListItem()
            item.post_id = post['code']
            item.publish_time = post['taken_at']*1000
            item.content = post['caption']['text']
            item.post_url = f"https://www.instagram.com/p/{post['code']}/"
            item.like_count = post['like_count']
            item.comment_count = post['comment_count']
            user_info = post['user']
            item.user_id = user_info['id']
            item.user_name = user_info['username']
            item.screen_name = user_info['full_name']
            item.avatar = user_info['hd_profile_pic_url_info']['url']
            item.image_list = [post['image_versions2']['candidates'][0]['url']]

            item.video_url = None
            item.video_cover_image = None
            item.video_duration = None
            item.play_count = None
            if post.get("video_versions"):
                item.video_url = post.get("video_versions")[0].get("url").replace('\\u0025', '%').replace('\\', "")
                video_cover_image = post.get("image_versions2", {}).get("candidates", [])
                if video_cover_image:
                    item.video_cover_image = video_cover_image[0].get("url").replace('\\u0025', '%').replace('\\', "")
                    item.image_list = None
                    item.video_duration = int(post.get("video_duration"))
                    item.play_count = post.get("play_count")

            print(item.__dict__)
            self.post_list.extend(item.__dict__)

            more_available = parse_data.get('more_available')

            if more_available:
                next_max_id = parse_data['next_max_id']
                while more_available and len(self.post_list) < post_num:
                    self.get_post_list(user_name, post_num, next_max_id)
        return self.post_list


if __name__ == '__main__':
    cookies = {
        'ig_did': '77AA134F-C3D2-4B9E-8504-D9E0CE4F7431',
        'datr': 'sCqeZhkjEb1BiI2gySOFjogH',
        'mid': 'Zp4qtAALAAGSqEN_ajk90p1Yc8Hv',
        'ig_nrcb': '1',
        'csrftoken': 'bX7sRQ5OjgTV6aTe5iolnAfSYsCNfKDV',
        'ds_user_id': '54091931721',
        'ps_n': '1',
        'ps_l': '1',
        'fbm_124024574287414': 'base_domain=.instagram.com',
        'dpr': '1.5',
        'sessionid': '54091931721%3Ay3wsGT9HbrL5Gd%3A0%3AAYfnAjzuDe0uz8N4P_seNt7POjUSSNEAOhn2dlBP58w',
        'rur': '"CCO\\05454091931721\\0541757405056:01f795f3bfe5cbc37968da1e8c3b6f25d5a8ef9640fc594c1cbb51cd2159cea2f1c614d6"',
        'wd': '1707x411',
    }
    post_list = InsPostList(cookies).get_post_list('junjun_jjj', 10)
