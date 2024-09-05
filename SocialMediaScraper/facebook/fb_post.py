import json
import re
import requests
from SocialMediaScraper.facebook import HEADERS
from SocialMediaScraper.models import FbPostItem, FbCommentItem
from SocialMediaScraper.utils import requests_with_retry, get_fb_dtsg


class FbPost:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS
        self.client_id = cookies['c_user']
        self.proxies = proxies
        self.fb_dtsg = get_fb_dtsg(cookies)
        self.image_list = []
        self.comment_list = []

    def get_post_detail(self, post_url):
        response = requests_with_retry.get(url=post_url, headers=self.headers, proxies=self.proxies).text
        if 'reaction_count' not in response:
            response = requests_with_retry.get(url=post_url, cookies=self.cookies, headers=self.headers,
                                               proxies=self.proxies).text
        if 'for (;;)' in response:
            raise Exception('cookie登录失效')
        item = FbPostItem()
        user_profile = re.findall(
            '"__typename":"User","__isActor":"User","id":"([^"]*?)","__isEntity":"User","url":"([^"]*?)".*?"name":"(['
            '^"]*?)","profile_picture":\{"uri":"([^"]*?)"',
            response)
        if not user_profile:
            user_profile = re.findall(
                '"__typename":"User","__isActor":"User","id":"([^"]*?)","__isEntity":"User","url":(null).*?"name":"(['
                '^"]*?)","profile_picture":\{"uri":"([^"]*?)"',
                response)
        _user_name = re.findall('<title>([^<]*?)</title>', response)
        if _user_name:
            _user_name = _user_name[0]
        _user_id = re.findall('"content_owner_id_new[^"]*?":[^"]*?"*(\d+)', response)
        if _user_id:
            _user_id = _user_id[0]
        _count = 0
        if user_profile:
            for user in user_profile:
                if user[2] in _user_name and _user_name:
                    _count += 1
                    item.user_id = user[0]
                    item.user_url = user[1].replace('\\', '')
                    item.user_name = user[2]
                    item.avatar = user[3].replace('\\', '')
                    if item.user_id.startswith("pfb"):
                        try:
                            item.user_id = re.findall('"content_owner_id_new[^"]*?":[^"]*?"(\d+)', response)[0]
                        except:
                            item.user_id = re.findall('"owning_profile_id":\s*"(\d+)', response)[0]
            if _count == 0:
                for user in user_profile:
                    if (user[0] == _user_id and _user_id) or user[0].startswith("pfb"):
                        _count += 1
                        item.user_id = user[0]
                        item.user_url = user[1].replace('\\', '')
                        item.user_name = user[2]
                        item.avatar = user[3].replace('\\', '')
                        if item.user_id.startswith("pfb"):
                            try:
                                item.user_id = re.findall('"content_owner_id_new[^"]*?":[^"]*?"(\d+)', response)[0]
                            except:
                                item.user_id = re.findall('"owning_profile_id":\s*"(\d+)', response)[0]
            if _count == 0:
                user = user_profile[0]
                item.user_id = user[0]
                item.user_url = user[1].replace('\\', '')
                item.user_name = user[2]
                item.avatar = user[3].replace('\\', '')
                if item.user_id.startswith("pfb"):
                    try:
                        item.user_id = re.findall('"content_owner_id_new[^"]*?":[^"]*?"(\d+)', response)[0]
                    except:
                        item.user_id = re.findall('"owning_profile_id":\s*"(\d+)', response)[0]

        if item.user_url == "null":
            item.user_url = f"https://www.facebook.com/profile.php?id={item.user_id}"

        item.post_url = post_url

        parent_feedback = re.findall('"parent_feedback":\s*\{\s*"id":\s*"([^"]*?)",', response)
        item.action_id = parent_feedback[0] if parent_feedback else None

        view_count = re.findall('"video_view_count":\s*(\d+)', response)
        item.view_count = int(view_count[0]) if view_count else None

        if item.action_id is None and item.view_count is not None:
            # 视频帖子
            item.action_id = \
                re.findall('"id":\s*"([^"]*?)",\s*"is_eligible_for_enhanced_comment_updates"', response)[0]
            # print(f'"play_count":\s*(\d+)\s*,\s*"id":\s*"{item["action_id"]}"')
            view_count = re.findall(f'"play_count":\s*(\d+)\s*,\s*"id":\s*"{item.action_id}"', response)
            item.view_count = int(view_count[0]) if view_count else None
            react_count = re.findall('"id":\s*"%s".*?"reaction_count":\s*\{\s*"count":\s*([^,]*?),' % item.action_id,
                                     response)
            item.react_count = int(react_count[0]) if react_count else None
            comment_count = re.findall('"id":\s*"%s".*?"comments":\s*\{\s*"total_count":\s*(\d+)' % item.action_id,
                                       response)
            item.comment_count = int(comment_count[0]) if comment_count else None
            share_count = re.findall('"id":\s*"%s".*?"share_count":\s*\{\s*"count":\s*([^,]*?),' % item.action_id,
                                     response)
            item.share_count = int(share_count[0]) if share_count else None

            # 视频页内容
            content = re.findall('"creation_story":.*?"message":\s*\{\s*"text":\s*"(.*?)",', response)
            item.content = content[0] if content else None
        else:
            # 非视频帖子
            react_count = re.findall('"reaction_count":\s*\{\s*"count":\s*([^,]*?),', response)
            item.react_count = int(react_count[0]) if react_count else None
            comment_count = re.findall('"comments":\s*\{\s*"total_count":\s*(\d+)', response)
            item.comment_count = int(comment_count[0]) if comment_count else None
            share_count = re.findall('"share_count":\s*\{\s*"count":\s*([^,]*?),', response)
            item.share_count = int(share_count[0]) if share_count else None
            view_count = re.findall('"video_view_count":\s*(\d+)', response)
            item.view_count = int(view_count[0]) if view_count else None

            content = re.findall('"footer_body":\s*"([^"]*?)"', response)
            if not content:
                content = re.findall('"message":\s*{\s*"__typename":\s*"TextWithEntities",\s*"text":\s*"(.*?)"},',
                                     response)
            item.content = content[0] if content else None

        create_time = re.findall('"metadata":\s*\[[^]]*?"creation_time":\s*(\d+),', response)
        item.create_time = int(create_time[0]) * 1000 if create_time else None
        if item.create_time is None:
            raise Exception('获取帖子发布时间失败，可能帖子链接失效导致')
        try:
            item.post_id = re.findall('"post_id":"([^"]+?)"', response)[0]
        except:
            raise Exception("获取帖子id错误")
        # 获取图片
        media_str = re.findall(
            '"attachment":\s*{\s*"mediaset_token":\s*"([^"]*?)",\s*"url":\s*"[^"]*?",\s*"all_subattachments":\s*\{\s*"count":\s*(\d+),\s*"nodes":\s*(\[[^]]*?\])',
            response)
        if media_str:
            mediaset_token = media_str[0][0]
            count = media_str[0][1]
            media_data = json.loads(media_str[0][2])
            for m in media_data:
                self.image_list.append(m['media']['viewer_image']['uri'])
            node_id = media_data[-1]['media']['id']
            if int(count) > len(self.image_list):
                self.get_more_image(node_id=node_id, mediasetToken=mediaset_token, count=int(count))
        if not self.image_list:
            self.image_list = [i.replace('\\', '') for i in
                               re.findall('"photo_image":\s*{\s*"uri":\s*"([^"]*?)"', response)]
        item.image_list = self.image_list if self.image_list else None

        # 获取视频
        video_str = re.findall('"browser_native_hd_url":\s*"([^"]*?)"', response)
        if not video_str:
            video_str = re.findall('"browser_native_sd_url":\s*"([^"]*?)"', response)
        item.video_url = video_str[0].replace('\\u0025', '%').replace('\\', "") if video_str else None
        if item.video_url:
            # 获取视频封面
            video_cover_image = re.findall(
                '"__typename":\s*"Video",\s*"preferred_thumbnail":\s*{\s*"image":\s*{\s*"uri":\s*"([^"]*?)"\s*}',
                response)
            item.video_cover_image = video_cover_image[0].replace(
                '\\u0025', '%').replace('\\', "") if video_cover_image else None

            # 获取视频时长
            video_duration_str = re.findall('"playable_duration_in_ms":\s*(\d+),', response)
            item.video_duration = int(int(video_duration_str[0]) / 1000) if video_duration_str else None
        else:
            item.video_cover_image = None
            item.video_duration = None
        # pprint(item)
        live_duration_str = re.findall('"broadcast_duration":\s*(\d+),', response)
        if live_duration_str:
            # 处理live
            item.content = re.findall('<title>([^<]*?) \|[^<]*?</title>', response)[0]
            video_duration_str = live_duration_str[0]
            item.video_duration = int(video_duration_str) if video_duration_str else None
            item.video_url = None
        return item.__dict__

    def get_more_image(self, node_id, mediasetToken, count=6):
        variables = {"isMediaset": True, "renderLocation": "permalink", "nodeID": node_id,
                     "mediasetToken": mediasetToken, "scale": 1, "feedLocation": "COMET_MEDIA_VIEWER",
                     "feedbackSource": 65, "focusCommentID": None, "glbFileURIHackToRenderAs3D_DO_NOT_USE": None,
                     "privacySelectorRenderLocation": "COMET_MEDIA_VIEWER", "useDefaultActor": False,
                     "useHScroll": False, "__relay_internal__pv__CometIsAdaptiveUFIEnabledrelayprovider": False,
                     "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": False,
                     "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                     "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False}

        data = {
            'av': self.client_id,
            '__aaid': '0',
            '__user': self.client_id,
            '__a': '1',
            '__req': 'o',
            '__hs': '19865.HYP:comet_pkg.2.1..2.1',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1013679676',
            '__s': '5m48k4:vy752m:mucgq1',
            '__hsi': '7371710829404852949',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg2owIxu13wFwhUngS3q2ibwNw9G2Saw8i2S1DwUx60GE3Qwb-q7oc81xoswMwto886C11wBz83WwgEcEhwGxu782lwv89kbxS2218wc61awkovwRwlE-U2exi4UaEW2uE5e7oqBwJK2W5olwUwgojUlDw-wUwxwjFovUaU3VBwFKq2-azo2NwwwOg2cwMwhEkxebwHwNxe6Uak0zU8oC1hxB0qo4e16wWwjHDzUiwRxW1fy8bU',
            '__csr': 'geAel7HlbikPtqlZvSjbii9tO8YR8OdQCRTHKDneytmltP9d4lvlvhkvqhBQjih6cmiaGAjIM-iZ4hoJp9UyiiidGUB28_QjJKVUWeFeUCp1aOABQZpemVprADGUO9zEhwNwKGm9xSdKEK9wiFrCXBxa3K2Cq7Eux6i5EV0jE-3qi0yo-1UxG4e1syEkwCwSy89o690ce0_o4Wew9i0lm3W1hxK1Jw4Kw5XwTKGxW0MU0AO05x-00yjvw0b_J07Dg1CE0TS0_9m022twqo0AS0jK04L8rw0FgCw2ho1AU047p02t4063Ec8gwTw4Ww2cU0xOcwSw0DFBo',
            '__comet_req': '15',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': '25638',
            'lsd': 'cpITrrhh2BWai3wSJeex5Q',
            '__spin_r': '1013679676',
            '__spin_b': 'trunk',
            '__spin_t': '1716360177',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'CometPhotoRootContentQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '7575004249243052',
        }

        response = requests.post('https://www.facebook.com/api/graphql/', cookies=self.cookies,
                                 headers=self.headers, proxies=self.proxies, data=data).text
        image = re.findall('"image":\s*\{\s*"uri":\s*"([^"]*?)"', response)[0].replace('\\', '')
        self.image_list.append(image)
        next_pid = re.findall(
            '"prevMedia":\s*\{\s*"edges":\s*\[\s*{\s*"node":\s*\{\s*"__typename":\s*"Photo",\s*"id":\s*"([^"]*?)"',
            response)
        if next_pid and len(self.image_list) < int(count):
            self.get_more_image(node_id=next_pid[0], mediasetToken=mediasetToken, count=count)

    def fb_comment(self, post_url, comment_num, end_cursor=None):
        action_id = self.get_post_detail(post_url).get('action_id')
        variables = {"commentsAfterCount": -1,
                     "commentsAfterCursor": end_cursor,
                     "commentsBeforeCount": None, "commentsBeforeCursor": None, "commentsIntentToken": None,
                     "feedLocation": "PERMALINK", "focusCommentID": None, "scale": 1.5, "useDefaultActor": False,
                     "id": action_id}

        data = {
            'av': self.client_id,
            '__aaid': '0',
            '__user': self.client_id,
            '__a': '1',
            '__req': '2n',
            '__hs': '19828.HYP2:comet_pkg.2.1..2.1',
            'dpr': '1.5',
            '__ccg': 'EXCELLENT',
            '__rev': '1012778326',
            '__s': 'dsbmb5:oil42p:dviofv',
            '__hsi': '7358077749270801986',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg2owIxu13wFwhUngS3q2ibwNw9G2Saw8i2S1DwUx60GE3Qwb'
                     '-q7oc81xoswMwto886C11wBz83WwgEcEhwGxu782lwv89kbxS2218wc61awko5m1mzXw8W58jwGzEaE5e7oqBwJK2W5olwUwgojUlDw-wUwxwjFovUaU3VBwFKq2-azo2NwwwOg2cwMwhEkxebwHwNxe6Uak0zU8oC1hxB0qo4e16wWwjHDzUiwRxW1fy8',
            '__csr': 'gbY8MRkaFl2YhOFiTT4h4IDkpA5nqEHTbbsRlsIJikqGKF4J5tdHjmQtpqBGi6i9b_paUy8VbGlpRy9rzGFGmGL'
                     '-58ydWzGWALxabQFm9FeF9AibgdUhALK9yVppVF8y2ii9yEy3muQm7oa8Su448whoqG79UC1pK2O9Bwtolx'
                     '-0zEOm3m1tz815Uc8hwqE4i14K0Pogw6ewcS080w4zymA1zw4yw27U4O0fxw0nSk7_w0f9G09Fw7Vgmg0zh19k08Xg0vCwyw7VweG0b7U0ngzE0Qd0a602yfw14603Z61kwh8KpkE16F-04po47y8098o',
            '__comet_req': '15',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': '25401',
            'lsd': 'A-PB38kuhgpUUVq9XfT3FQ',
            '__spin_r': '1012778326',
            '__spin_b': 'trunk',
            '__spin_t': '1713185978',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'CommentsListComponentsPaginationQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '25001741399469692',
        }
        response = requests_with_retry.post('https://www.facebook.com/api/graphql/', cookies=self.cookies,
                                            headers=self.headers, proxies=self.proxies, data=data).text
        if 'for (;;)' in response:
            raise Exception('cookie登录失效')
        try:
            data = json.loads(response)['data']['node']['comment_rendering_instance_for_feed_location']['comments']
            edges = data['edges']
            page_info = data['page_info']
        except:
            _list = response.split('\n')
            edges = []
            for _resp in _list:
                try:
                    data = json.loads(_resp)['data']['node']['comment_rendering_instance_for_feed_location']['comments']
                except:
                    continue
                edges.extend(data['edges'])
                page_info = data['page_info']
        for edge in edges:
            item = FbCommentItem()
            item.comment_id = edge['node'].get('legacy_fbid')
            item.gender = edge['node']['author']['gender']
            item.user_id = edge['node']['author']['id']
            item.user_name = edge['node']['author']['name']
            item.user_url = edge['node']['author']['url']
            item.avatar = edge['node']['author']['profile_picture_depth_0']['uri']
            item.content = edge['node']['body'] if not edge['node']['body'] else edge['node']['body']['text']
            item.likes_count = edge['node']['feedback']['reactors']['count']
            item.create_time = int(edge['node']['created_time']) * 1000
            self.comment_list.append(item.__dict__)
        if len(self.comment_list) < comment_num and page_info['has_next_page']:
            self.fb_comment(action_id, comment_num, page_info['end_cursor'])
        return self.comment_list
