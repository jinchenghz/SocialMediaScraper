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
            item.publish_time = post['taken_at'] * 1000
            item.content = post['caption']['text']
            item.post_url = f"https://www.instagram.com/p/{post['code']}/"
            item.like_count = post['like_count']
            item.comment_count = post['comment_count']
            user_info = post['user']
            item.user_id = user_info['id']
            item.user_name = user_info['username']
            item.screen_name = user_info['full_name']
            item.avatar = user_info['hd_profile_pic_url_info']['url']

            if post.get("video_versions"):
                item.video_url = post.get("video_versions")[0].get("url").replace('\\u0025', '%').replace('\\', "")
                video_cover_image = post.get("image_versions2", {}).get("candidates", [])
                if video_cover_image:
                    item.video_cover_image = video_cover_image[0].get("url").replace('\\u0025', '%').replace('\\', "")
                    item.image_list = None
                    item.video_duration = int(post.get("video_duration"))
                    item.play_count = post.get("play_count")
            else:
                if post.get("carousel_media") is None:
                    item.image_list = [post['image_versions2']['candidates'][0]['url']]
                else:
                    item.image_list = [image["image_versions2"]["candidates"][0]["url"] for image in
                                       post['carousel_media']]
                item.video_url = None
                item.video_cover_image = None
                item.video_duration = None
                item.play_count = None
            print(item.__dict__)
            self.post_list.extend(item.__dict__)

            more_available = parse_data.get('more_available')

            if more_available:
                next_max_id = parse_data['next_max_id']
                while more_available and len(self.post_list) < post_num:
                    self.get_post_list(user_name, post_num, next_max_id)
        return self.post_list

