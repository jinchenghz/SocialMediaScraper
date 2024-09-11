import json
import requests
from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.instagram.utils import get_X_IG_App_ID
from SocialMediaScraper.models import InsSearchItem


class InsSearch:
    def __init__(self, cookies=None, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({'x-csrftoken': cookies['csrftoken'], 'x-ig-app-id': get_X_IG_App_ID(cookies)})
        self.post_list = []

    def hashtag_post(self, keyword, post_num):
        params = {
            'tag_name': keyword,
        }
        try:
            response = requests.get('https://www.instagram.com/api/v1/tags/web_info/', params=params,
                                    cookies=self.cookies, headers=self.headers, proxies=self.proxies).text
            response = json.loads(response)
        except:
            return []
        sections = response['data']['top']['sections']
        for section in sections:
            _media_list = section['layout_content'].get('fill_items')
            if not _media_list:
                _media_list = section['layout_content'].get('medias')
            for _media in _media_list:
                if len(self.post_list) >= post_num:
                    return self.post_list
                media = _media['media']
                item = InsSearchItem()
                item.post_id = media['code']
                item.post_url = f"https://www.instagram.com/p/{item.post_id}/"
                item.content = media['caption']['text']
                item.publish_time = media['caption']['created_at'] * 1000
                item.user_id = media['caption']['user_id']
                item.user_full_name = media['caption']['user']['full_name']
                item.user_name = media['caption']['user']['username']
                item.user_url = f"https://www.instagram.com/{item.user_name}/"
                item.avatar = media['caption']['user']['profile_pic_url']
                if not media.get('carousel_media'):
                    item.image_list = [media['image_versions2']['candidates'][0]['url']]
                else:
                    item.image_list = [media['image_versions2']['candidates'][0]['url'] for media in
                                       media['carousel_media']]
                item.like_count = media['like_count']
                item.comment_count = media['comment_count']
                item.play_count = media.get('play_count')

                # 抓取视频
                item.video_url = None
                item.video_cover_image = None
                item.video_duration = None

                if media.get("video_versions"):
                    item.video_url = media['video_versions'][0]['url']
                    item.video_cover_image = media['image_versions2']['candidates'][0]['url']
                    item.video_duration = int(media['video_duration'])

                self.post_list.append(item.__dict__)
        return self.post_list
