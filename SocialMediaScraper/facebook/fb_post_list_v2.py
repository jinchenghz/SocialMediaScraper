import json
import re
from jsonpath_ng import parse
from SocialMediaScraper.models import FbPostListItem
from SocialMediaScraper.utils import HEADERS, requests_with_retry, get_fb_dtsg


class FbPostList:
    def __init__(self, cookies, post_num=0, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS
        self.client_id = self.cookies['c_user']
        self.proxies = proxies
        self.fb_dtsg = get_fb_dtsg(self.cookies)
        self.image_list = []
        self.post_list = []
        self.post_num = post_num

    def get_user_info(self, url):
        response = requests_with_retry.get(f'{url}about', cookies=self.cookies, headers=self.headers).text
        item = dict()
        user_id = re.findall('"userID":\s*"(\d+)"', response)
        item['user_id'] = user_id[0] if user_id else None
        # (item)
        return item

    def get_post_list(self, userId, cursor=None):
        try:
            userId = str(int(userId))
        except:
            if userId.startswith('http'):
                userId = userId + '/' if not userId.endswith('/') else userId
                userId = self.get_user_info(userId)['user_id']
            else:
                userId = self.get_user_info(f"https://www.facebook.com/{userId}/")['user_id']
        variables = {"count": 1, "feedbackSource": 0, "feedLocation": "TIMELINE", "omitPinnedPost": True,
                     "privacySelectorRenderLocation": "COMET_STREAM", "renderLocation": "timeline", "scale": 1.5,
                     "userID": userId, "postedBy": {"group": "OWNER"},
                     "__relay_internal__pv__VideoPlayerRelayReplaceDashManifestWithPlaylistrelayprovider": True,
                     "__relay_internal__pv__IsWorkUserrelayprovider": False,
                     "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
                     "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                     "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": False,
                     "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
                     "__relay_internal__pv__StoriesTrayShouldShowMetadatarelayprovider": False,
                     "__relay_internal__pv__StoriesRingrelayprovider": False,
                     "__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider": False}
        data = {
            'av': self.client_id,
            '__aaid': '0',
            '__user': self.client_id,
            '__a': '1',
            '__req': '16',
            '__hs': '19816.HYP2:comet_pkg.2.1..2.1',
            'dpr': '1.5',
            '__ccg': 'EXCELLENT',
            '__rev': '1012503000',
            '__s': 'd7zgan:olerv1:g2wccc',
            '__hsi': '7353522613855639510',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg2owIxu13wFwnUW3q2ibwNwnof8boG0x8bo6u3y4o2Gwn82nwb-q7oc81xoswIK1Rwwwqo462mcwfG12wOx62G5Usw9m1YwBgK7o884y0Mo4G1hx-3m1mzXw8W58jwGzE8FU5e7oqBwJK2W5olwUwgojUlDw-wUwxwjFovUaU3qxWm2CVEbUGdwr84i223908O3216xi4UK2K364UrwFg2fwxyo566k1FwgU4q3G1eKufxa3m7E',
            '__csr': 'gcysQIpqTEt5RNImJEIABtOql8Ip5NJQysG8RiZlHlPOFOQIAAOlhlWLSijle_Fqhml4WAZvhiGp3FokykyD_yVfzarx6bKcDLLAKVaFt4jKi8GuGAh9pKVGAoKvzEF4CGaJ29poKUG8-GwFUa9pox3VaxrxN1udxrixvCyeqi2a8G13UXx65o89E-4UowlUqwtGwRwxz86afxu5odES2e9wu82ewn8fE8E2iAwTwyway0M84C783dwjo1JE1ZE38wvqg1NE0xe086zaw0j3U7i7U0109kEiw2s-aFk3x07gxa0LE0kUw1lu2xBy40oO0Po04l-0r6m0Oo0Cd00D_w0RPIyw47yE4Zw9604I85m2O9w',
            '__comet_req': '15',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': '25312',
            'lsd': 'ux-QHv_wEXKcYHCFwet_jG',
            '__spin_r': '1012503000',
            '__spin_b': 'trunk',
            '__spin_t': '1712125403',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometTimelineFeedQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '25041810422129502',
        }

        response = requests_with_retry.post('https://www.facebook.com/api/graphql/', cookies=self.cookies,
                                            headers=self.headers, proxies=self.proxies, data=data).text
        if 'for (;;)' in response:
            raise Exception('cookie登录失效')
        json_list = response.split('\n')
        for _json in json_list:
            if '"timeline_list_feed_units":' in _json:
                data = json.loads(_json)
                edges = data['data']['user']['timeline_list_feed_units']['edges']
                for edge in edges:
                    item = FbPostListItem()
                    item.post_id = edge['node']['post_id']
                    comet_sections = edge['node']['comet_sections']
                    item.content = comet_sections['content']['story']['comet_sections']['message'][
                        'story']['message']['text']
                    item.publish_time = parse("$..creation_time").find(comet_sections)[0].value
                    story_list = parse("$..story").find(comet_sections)
                    for story in story_list:
                        story_data = story.value
                        if story_data.get("creation_time"):
                            item.post_url = story_data.get("url")
                    self.post_list.append(item.__dict__)
                    print(item.__dict__)
                if len(edges):
                    cursor = edges[-1]['cursor']
                    print('cursor', cursor)
                    if cursor and len(self.post_list) < self.post_num:
                        self.get_next_post(userId, cursor=cursor)

        return self.post_list

    def get_next_post(self, user_id, cursor):
        variables = {"afterTime": None, "beforeTime": None, "count": 3, "cursor": cursor,
                     "feedLocation": "TIMELINE",
                     "feedbackSource": 0, "focusCommentID": None, "memorializedSplitTimeFilter": None,
                     "omitPinnedPost": True, "postedBy": {"group": "OWNER"}, "privacy": None,
                     "privacySelectorRenderLocation": "COMET_STREAM", "renderLocation": "timeline", "scale": 1.5,
                     "stream_count": 1, "taggedInOnly": None, "useDefaultActor": False, "id": user_id,
                     "__relay_internal__pv__VideoPlayerRelayReplaceDashManifestWithPlaylistrelayprovider": True,
                     "__relay_internal__pv__IsWorkUserrelayprovider": False,
                     "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
                     "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                     "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": False,
                     "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
                     "__relay_internal__pv__StoriesTrayShouldShowMetadatarelayprovider": False,
                     "__relay_internal__pv__StoriesRingrelayprovider": False,
                     "__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider": False}

        data = {
            'av': self.client_id,
            '__aaid': '0',
            '__user': self.client_id,
            '__a': '1',
            '__req': '1e',
            '__hs': '19816.HYP2:comet_pkg.2.1..2.1',
            'dpr': '1.5',
            '__ccg': 'EXCELLENT',
            '__rev': '1012503000',
            '__s': 'd7zgan:olerv1:g2wccc',
            '__hsi': '7353522613855639510',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg2owIxu13wFwnUW3q2ibwNwnof8boG0x8bo6u3y4o2Gwn82nwb-q7oc81xoswIK1Rwwwqo462mcwfG12wOx62G5Usw9m1YwBgK7o884y0Mo4G1hx-3m1mzXw8W58jwGzE8FU5e7oqBwJK2W5olwUwgojUlDw-wSU8o4Wm7-2K0SEuBwFKq2-azo6O14wwwOg2cwMwhEkxebwHwNxe6Uak0zU8oC1hxB0qo4e16wWwjHDzUiwRxW',
            '__csr': 'gcy12whR7NqTd999sCBib6hsrt8AW8RiZlHlPOFOQIAAOlhlWLTGjle_FqhnJ4WWYDhiGgwXK4bykyD_yaA-cFKqaya-qmu--iXWGBQheVaBGuGAh9pKVGAoKvzEF4CGaJ29poKUG8-GwFUa9pox3VaxrxN1udxrixvCyeqi2a8G2qUoUXx65o89E-4UowhU-6E7qEdo8oO1yzUnxm68tzo8UC2y1aAw8W1sw-wyw9ai3u2a1MwTwc219xO0Po4S0rq0ukEO0O87SA0sq08jw21EOGw0j387i7U0eO87i00MVQEiw2s-aFk3x07gxa0LE0kUw1lu2xBy40oO0Po04l-0r6m0Oo0Cd00D_w0RPIywbO1ayE4Zw9604I85m2O9w1Jq',
            '__comet_req': '15',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': '25312',
            'lsd': 'ux-QHv_wEXKcYHCFwet_jG',
            '__spin_r': '1012503000',
            '__spin_b': 'trunk',
            '__spin_t': '1712125403',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometTimelineFeedRefetchQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '25124212063860761',
        }
        response = requests_with_retry.post('https://www.facebook.com/api/graphql/', cookies=self.cookies,
                                            headers=self.headers, proxies=self.proxies, data=data).text
        if 'for (;;)' in response:
            raise Exception('cookie登录失效')

        json_list = response.split('\n')
        cursor = None
        __edge_list = []
        for _json in json_list:
            if '"timeline_list_feed_units":' in _json:
                data = json.loads(_json)
                edges = data['data']['node']['timeline_list_feed_units']['edges']
                for edge in edges:
                    __edge_list.append(edge)

            elif '"creation_time"' in _json:
                __edge_list.append(json.loads(_json)['data'])

        for edge in __edge_list:
            item = FbPostListItem()
            item.post_id = edge['node']['post_id']
            comet_sections = edge['node']['comet_sections']
            try:
                item.content = comet_sections['content']['story']['comet_sections']['message'][
                    'story']['message']['text']
            except:
                item.content = None
            item.publish_time = parse("$..creation_time").find(comet_sections)[0].value
            story_list = parse("$..story").find(comet_sections)
            for story in story_list:
                story_data = story.value
                if story_data.get("creation_time"):
                    item.post_url = story_data.get("url")
            self.post_list.append(item.__dict__)
            print(item.__dict__)
            if edge.get("cursor"):
                cursor = edge.get("cursor")
        print('cursor', cursor)
        if cursor and len(self.post_list) < self.post_num:
            self.get_next_post(user_id, cursor=cursor)

