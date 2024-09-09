import json
import re
from SocialMediaScraper.instagram import HEADERS
from SocialMediaScraper.instagram.utils import get_fb_dtsg, get_X_IG_App_ID
from SocialMediaScraper.models import InsPostItem, InsCommentItem
from SocialMediaScraper.utils import requests_with_retry


class InsPost:
    def __init__(self, cookies, **kwargs):
        self.headers = HEADERS.copy()
        self.headers.update({'x-csrftoken': cookies['csrftoken'], 'x-ig-app-id': get_X_IG_App_ID(cookies)})
        self.cookies = cookies
        self.proxies = kwargs.get("proxies")
        self.comment_list = []
        self.media_id = None

    def ins_post_detail(self, post_id):
        if post_id.startswith('https://www.instagram.com/p/'):
            post_id = re.findall('/p/([^/]+)?', post_id)[0]
        post_info = InsPostItem()
        fb_dtsg = get_fb_dtsg(code=post_id, cookie=self.cookies)
        if fb_dtsg == '':
            raise Exception("账号异常")

        variables = {"shortcode": post_id, "__relay_internal__pv__PolarisShareMenurelayprovider": False}

        data = {
            '__d': 'www',
            '__user': '0',
            '__a': '1',
            '__req': 't',
            '__hs': '19797.HYP:instagram_web_pkg.2.1..0.1',
            'dpr': '2',
            '__ccg': 'UNKNOWN',
            '__rev': '1012067416',
            '__s': 'a8vbyw:kaig07:e7422u',
            '__hsi': '7346409357632396275',
            '__dyn': '7xeUjG1mxu1syUbFp40NonwgU7SbzEdF8aUco2qwJxS0k24o0B-q1ew65xO0FE2awt81s8hwGwQwoEcE7O2l0Fwqo31w9O7U2cxe0EUjwGzEaE7622362W2K0zK5o4q3y1Sx-0iS2Sq2-azo7u1xwIw8O321LwTwKG1pg2Xwr86C1mwrd6goK68jDyUrAwHyokw',
            '__csr': 'g9tJ9ginOTbcRPiQkrbRAujFjFikQKpDcNHtqG9z6qVbiZ7O4gKSUyGxqjAjQGV_J4mcFa9VuvJk8ALhqGal3Ful7CGEG9BHGh4ypFoHpQbrAmq444WWye8AK8KEGq48W2ah7U01k6Xbw6Mwau0CUixjzU0hrw1MxADgzAo28iyN3x3efwAxqdwkA0emw2Ok63xi0fPw71gaUbGx51jg02hWw',
            '__comet_req': '7',
            'fb_dtsg': fb_dtsg,
            'jazoest': '26421',
            'lsd': 'M44qCrr_iiyLwW2cAD6Ai8',
            '__spin_r': '1012067416',
            '__spin_b': 'trunk',
            '__spin_t': '1710469219',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'PolarisPostRootQuery',
            'variables': json.dumps(variables, ensure_ascii=False),
            'server_timestamps': 'true',
            'doc_id': '25369833802607926',
        }
        response = requests_with_retry.post('https://www.instagram.com/api/graphql', cookies=self.cookies,
                                            headers=self.headers, data=data, proxies=self.proxies)
        if 'for (;;)' in response.text:
            raise Exception("账号异常")
        try:
            parsed_data = json.loads(response.text)
        except:
            raise Exception("IP被ins封禁")
        post_info_data = parsed_data['data']['xdt_api__v1__media__shortcode__web_info']['items'][0]
        try:
            text = post_info_data['caption']['text']
        except:
            text = None
        try:
            create_time = post_info_data['caption']['created_at']
        except:
            create_time = post_info_data['taken_at']

        post_info.media_id = post_info_data['pk']
        post_info.content = text
        post_info.publish_time = create_time
        post_info.like_count = post_info_data['like_count']
        post_info.comment_count = post_info_data['comment_count']
        post_info.post_url = f'https://www.instagram.com/p/{post_info_data["code"]}'

        if post_info_data.get('coauthor_producers') and isinstance(post_info_data.get('coauthor_producers'), list):
            post_info.coauthor_producers = []
            for i in post_info_data.get('coauthor_producers'):
                coauthor_producers = dict()
                coauthor_producers['user_id'] = i["id"]  # 数字型
                coauthor_producers['user_name'] = i["username"]
                coauthor_producers['screen_name'] = i["full_name"] if i.get("full_name") else i["username"]
                coauthor_producers['avatar'] = i["profile_pic_url"]
                post_info.coauthor_producers.append(coauthor_producers)
            if not post_info.coauthor_producers:
                user_name = post_info_data['user']['username']
                user_id = post_info_data['user']['id']
                pic = post_info_data['user']['profile_pic_url']
                post_info.user_id = user_id
                post_info.user_name = user_name
                post_info.screen_name = post_info_data['user']['full_name'] if post_info_data['user'].get(
                    'full_name') else user_name
                post_info.avatar = pic

        else:
            user_name = post_info_data['user']['username']
            user_id = post_info_data['user']['id']
            pic = post_info_data['user']['profile_pic_url']
            post_info.user_id = user_id
            post_info.user_name = user_name
            post_info.screen_name = post_info_data['user']['full_name'] if post_info_data['user'].get(
                'full_name') else user_name
            post_info.avatar = pic

        # 获取视频以及图片
        carousel_media = post_info_data.get('carousel_media')
        carousel_media = carousel_media if carousel_media else []
        image_list = []
        video_str = None
        if not carousel_media:
            image_list = [post_info_data['image_versions2']['candidates'][0]['url'].replace('\\', "")]
        else:
            for m in carousel_media:
                video_str = m.get('video_dash_manifest')
                if not video_str:
                    image_list.append(m['image_versions2']['candidates'][0]['url'].replace('\\', ""))

        post_info.image_list = image_list if image_list else None
        if not video_str:
            video_str = post_info_data.get('video_dash_manifest')
        video_str = video_str if video_str else ''
        video_data = [i.replace('&amp;', '&').replace('\\u0025', '%').replace('\\', "") for i in
                      re.findall('<BaseURL>([^<]*?)\u003C', video_str)]
        post_info.video_url = video_data[0] if video_data else None

        if post_info.video_url:
            video_cover_image = post_info_data.get("image_versions2", {}).get("candidates", [])
            if video_cover_image:
                video_cover_image = video_cover_image[0].get("url").replace('\\u0025', '%').replace('\\', "")
            post_info.video_cover_image = video_cover_image if video_cover_image else None

            # 获取视频时长
            video_duration_str = re.findall('duration="PT(\d+.\d+)S"',
                                            post_info_data.get('video_dash_manifest', ''))
            post_info.video_duration = int(float(video_duration_str[0])) if video_duration_str else None

        else:
            post_info.video_cover_image = None
            post_info.video_duration = None

        return post_info.__dict__

    def get_comments(self, post_id, comment_num, next_min_id=None):
        if not self.media_id:
            self.media_id = self.ins_post_detail(post_id).get("media_id")
        if next_min_id:
            params = {
                'can_support_threading': 'true',
                'min_id': next_min_id,
                'sort_order': 'popular',
            }
        else:
            params = {
                'can_support_threading': 'true',
                'permalink_enabled': 'false',
            }
        print('self.media_id', self.media_id)
        response = requests_with_retry.get(f'https://www.instagram.com/api/v1/media/{self.media_id}/comments/',
                                           params=params, cookies=self.cookies, headers=self.headers,
                                           proxies=self.proxies)

        try:
            parse_data = json.loads(response.text)
        except:
            raise Exception("IP被ins封禁")

        status = parse_data['status']
        if status != 'ok':
            raise Exception("获取评论失败")
        else:
            comments = parse_data['comments']
            for comment in comments:
                comment_info = InsCommentItem()
                comment_info.comment_id = comment.get('pk')
                comment_info.user_id = comment['user']['id']
                comment_info.user_name = comment['user']['username']
                comment_info.screen_name = comment['user']['full_name'] if comment['user']['full_name'] else \
                    comment_info.user_name
                comment_info.avatar = comment['user']['profile_pic_url']
                comment_info.comment_content = comment['text']
                comment_info.create_time = comment['created_at']
                comment_info.like_num = comment['comment_like_count']
                self.comment_list.append(comment_info.__dict__)

            has_more_headload_comments = parse_data['has_more_headload_comments']
            if has_more_headload_comments and len(self.comment_list) < comment_num:
                self.get_comments(post_id, comment_num, parse_data['next_min_id'])
            return self.comment_list
