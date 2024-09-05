import json
import re

from SocialMediaScraper.facebook import HEADERS
from SocialMediaScraper.utils import requests_with_retry, get_fb_dtsg


class FBSearch:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.client_id = self.cookies['c_user']
        self.proxies = proxies
        self.fb_dtsg = get_fb_dtsg(cookies)
        self.post_list = []

    def fb_search_post(self, keyword, post_num, cursor=None):
        variables = {"count": 5, "allow_streaming": False,
                     "args": {"callsite": "COMET_GLOBAL_SEARCH",
                              "config": {"exact_match": False,
                                         "high_confidence_config": None,
                                         "intercept_config": None,
                                         "sts_disambiguation": None,
                                         "watch_config": None}, "context": {
                             "bsid": "02140da1-c95e-4757-9c34-c9b316b7ab3a", "tsid": "0.35488376016632106"},
                              "experience": {"client_defined_experiences": [],
                                             "encoded_server_defined_params": None,
                                             "fbid": None, "type": "POSTS_TAB"},
                              "filters": [], "text": keyword}, "cursor": cursor,
                     "feedbackSource": 23, "fetch_filters": True, "renderLocation": "search_results_page", "scale": 1,
                     "stream_initial_count": 0, "useDefaultActor": False,
                     "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
                     "__relay_internal__pv__IsWorkUserrelayprovider": False,
                     "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
                     "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                     "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": False,
                     "__relay_internal__pv__CometIsAdaptiveUFIEnabledrelayprovider": False,
                     "__relay_internal__pv__IncludeCommentWithAttachmentrelayprovider": True,
                     "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
                     "__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider": False}

        data = {
            'av': self.client_id,
            '__aaid': '0',
            '__user': self.client_id,
            '__a': '1',
            '__req': '1p',
            '__hs': '19907.HYP:comet_pkg.2.1..2.1',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1014644081',
            '__s': 'tniz8c:3eq2ym:y7f1mj',
            '__hsi': '7387291773398703860',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C17xt3odE98K361twYwJyE24wJwpUe8hwaG0Z82_CxS320om78bbwto886C11wBz83WwgEcEhwGxu782lwv89kbxS1Fwc61awkovwRwlE-U2exi4UaEW2au1jwUBwJK2W5olwUwgojUlDw-wUwxwjFovUaU6a1TxWm2CVEbUGdwb6223908O3216xi4UK2K364UrwFg2fwxyo566k1FwgU4q3G1eKufxa3mUqwjUy2-2K',
            '__csr': 'g9Ir2Ijdbb18I_tPR6syShROqOW8Ddqs8W4q8Ghv9sYRiibh3bkpOv99dRcizW-Vdqj-fiZaZqhHKlaXAFqhkqBAjKUKQllCVe-V9994bAF4-rFfKhVFVrx6mVAFecAhoymWLQquibUpxeU-mFFEN0UyEK7rxeh1-5ojyoiy88EKi3uq2SexK6EqzA5o24yEjyEe8S3iaxi1jwaO2a1Txe2WE2SwhU5W1Qw5kwi8cE14U3jw1xq08Zwb22q0xE049bxy00gwCq1xCm0ayg1F80wS0bgw1tu9yE0Em0pmewyw31Eiw0V4xG01aWg0pww9q0cLK7E0LmU72033Uw',
            '__comet_req': '15',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': '25704',
            'lsd': 'DMtnb9JctlQicRvlCso18z',
            '__spin_r': '1014644081',
            '__spin_b': 'trunk',
            '__spin_t': '1719987898',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'SearchCometResultsInitialResultsQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '26293763366881390',
        }

        response = requests_with_retry.post('https://www.facebook.com/api/graphql/', cookies=self.cookies,
                                            headers=HEADERS, data=data, proxies=self.proxies).text
        # print(response)
        data = json.loads(response.split('\n')[0])
        edges = data['data']['serpResponse']['results']['edges']
        for edge in edges:
            if edge['node']['role'] != 'TOP_PUBLIC_POSTS':
                continue
            item = dict()
            item['post_id'] = edge['relay_rendering_strategy']['view_model']['click_model']['story']['post_id']
            comet_sections = edge['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']
            story = comet_sections['content']['story']
            item['action_id'] = story['feedback']['id']
            try:
                item['content'] = story['message']['text']
            except:
                item['content'] = ''

            actor = comet_sections['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]
            item['user_name'] = actor['name']
            item['user_id'] = actor['id']
            item['user_url'] = actor['url']
            item['avatar'] = actor['profile_picture']['uri']
            metadata = comet_sections['context_layout']['story']['comet_sections']['metadata']
            for meta in metadata:
                if meta.get("story", {}).get("creation_time") and meta.get("story", {}).get("creation_time"):
                    item['create_time'] = meta['story']['creation_time'] * 1000
                    item['post_url'] = meta['story']['url']
                    break

            if not item.get('create_time'):
                raise Exception('create_time not found')
            try:
                reaction = comet_sections['feedback']['story']['comet_feed_ufi_container']['story']['feedback_context'][
                    'feedback_target_with_context']['ufi_renderer']['feedback'][
                    'comet_ufi_summary_and_actions_renderer'][
                    'feedback']
            except:
                reaction = comet_sections['feedback']['story']['comet_feed_ufi_container']["story"][
                    "story_ufi_container"]['story']['feedback_context']['feedback_target_with_context'][
                    'comet_ufi_summary_and_actions_renderer']['feedback']
            item['like_count'] = reaction['i18n_reaction_count']
            item['share_count'] = reaction['i18n_share_count']
            item['comment_count'] = reaction['comment_rendering_instance']['comments']['total_count']
            # 爬取图片以及视频
            item['image_list'] = []
            item['video_list'] = []
            item['video_cover_image'] = []
            item['duration'] = []
            if story['attachments']:
                attachment = story['attachments'][0]['styles']['attachment']
                if attachment.get("all_subattachments"):
                    media_nodes = attachment['all_subattachments']['nodes']
                    for node in media_nodes:
                        if not node.get('media'):
                            continue
                        if node['media']['__typename'] == 'Photo':
                            if node['media']['viewer_image'].get('uri'):
                                item['image_list'].append(node['media']['viewer_image']['uri'])
                            else:
                                item['image_list'].append(node['media']['photo_image']['uri'])
                        if not attachment.get('media'):
                            continue
                        elif attachment['media']['__typename'] == 'Video':
                            item['image_list'].append(attachment['media']['thumbnailImage']['uri'])
                            video_url = node['media']['browser_native_hd_url']
                            if not video_url:
                                video_url = node['media']['browser_native_sd_url']
                            item['video_list'].append(video_url)
                            item['video_cover_image'].append(node['media']['preferred_thumbnail']['image']['uri'])
                            item['duration'].append(int(node['media']['playable_duration_in_ms']/1000))

                else:
                    if not attachment.get('media'):
                        continue
                    if attachment['media']['__typename'] == 'Photo':
                        if attachment['media']['viewer_image'].get('uri'):
                            item['image_list'].append(attachment['media']['viewer_image']['uri'])
                        else:
                            item['image_list'].append(attachment['media']['photo_image']['uri'])
                    elif attachment['media']['__typename'] == 'Video':
                        item['image_list'].append(attachment['media']['thumbnailImage']['uri'])
                        video_url = attachment['media']['browser_native_hd_url']
                        if not video_url:
                            video_url = attachment['media']['browser_native_sd_url']
                        item['video_list'].append(video_url)

                        item['video_cover_image'].append(attachment['media']['preferred_thumbnail']['image']['uri'])
                        item['duration'].append(int(attachment['media']['playable_duration_in_ms'] / 1000))

            self.post_list.append(item)

        page_info = data['data']['serpResponse']['results']['page_info']
        if page_info.get('has_next_page') and page_info.get('end_cursor') and len(self.post_list) < post_num:
            # 请求下一页
            self.fb_search_post(keyword, post_num, page_info['end_cursor'])
        return self.post_list

