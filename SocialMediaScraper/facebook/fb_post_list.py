import json
import re
from SocialMediaScraper.utils import HEADERS, requests_with_retry, get_fb_dtsg


class FbPostList:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS
        self.client_id = self.cookies['c_user']
        self.proxies = proxies
        self.fb_dtsg = get_fb_dtsg(self.cookies)
        self.image_list = []

    def get_user_info(self, url):
        response = requests_with_retry.get(f'{url}about', cookies=self.cookies, headers=self.headers).text
        item = dict()
        item['user_url'] = 'https://www.facebook.com/RocksRolls/about'
        user_id = re.findall('"userID":\s*"(\d+)"', response)
        item['user_id'] = user_id[0] if user_id else None
        name = re.findall("<title>([^<]*?)</title>", response)
        item['name'] = name[0] if name else None
        friends = re.findall('"text":\s*"(\d[^"]*?)\sfriends"', response)
        item['friends'] = friends[0] if friends else None
        followers = re.findall('"text":\s*"(\d[^"]*?)\sfollowers"', response)
        item['followers'] = followers[0] if followers else None
        likes = re.findall('"text":\s*"(\d[^"]*?)\slikes"', response)
        item['likes'] = likes[0] if likes else None
        following = re.findall('"text":\s*"(\d[^"]*?)\sfollowing"', response)
        item['following'] = following[0] if following else None
        location = re.findall('"text":\s*"Lives in ([^"]*?)"', response)
        item['location'] = location[0] if location else None
        profile_pic = re.findall('"profilePicLarge":\s*\{\s*"uri":\s*"([^"]*?)"', response)
        item['profile_pic'] = profile_pic[0].replace("\\", "") if profile_pic else None
        gender = re.findall('"gender":\s*"([^"]*?)"', response)
        item['gender'] = gender[0] if gender else None
        # (item)
        return item

    def get_post_list(self, userId, post_num):
        try:
            userId = str(int(userId))
        except:
            if userId.startswith('http'):
                userId = userId + '/' if not userId.endswith('/') else userId
                userId = self.get_user_info(userId)['user_id']
            else:
                userId = self.get_user_info(f"https://www.facebook.com/{userId}/")['user_id']
        print('userId:', userId)
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
            # 'fb_dtsg': "NAcPVwq1O1BuFeOiFEyR5rpFXMmBlQ3RSgxvZ5-Da3ujDNnozWjbrtw:45:1701856486",
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
                                            headers=self.headers,
                                            proxies=self.proxies, data=data).text
        # print(response)
        if 'for (;;)' in response:
            raise Exception('cookie登录失效')
        post_url_list = []
        ret = re.findall(
            '"actors":\[\{"__typename":"User","id":["]*(\d+)["]*[^]]*?],.*?(?="ghl_mocked_encrypted_link)[^,]*?,"ghl_label_mocked_cta_button"[^,]*?,"wwwURL":"([^"]*?)"',
            response)
        for r in ret:
            if str(r[0]) == str(userId):
                post_url_list.append(r[1].replace('\\', ''))

        end_cursor = re.findall('"has_next_page":true,"end_cursor":"([^"]*?)"', response)
        for i in range(20):
            if end_cursor:
                # print('翻页cursor:', end_cursor)
                _post_url_list, end_cursor = self.get_next_post(userId, end_cursor[0])
                print('翻页:', _post_url_list, end_cursor)
                post_url_list.extend(_post_url_list)
                if not end_cursor or len(post_url_list) >= int(post_num):
                    break
            else:
                break
        return post_url_list

    def get_next_post(self, user_id, end_cursor):
        variables = {"afterTime": None, "beforeTime": None, "count": 3, "cursor": end_cursor,
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
        post_url_list = []
        ret = re.findall(
            '"actors":\[\{"__typename":"User","id":["]*(\d+)["]*[^]]*?],.*?(?="ghl_mocked_encrypted_link)[^,]*?,"ghl_label_mocked_cta_button"[^,]*?,"wwwURL":"([^"]*?)"',
            response)
        for r in ret:
            if str(r[0]) == str(user_id):
                post_url_list.append(r[1].replace('\\', ''))

        end_cursor = re.findall('"has_next_page":true,"end_cursor":"([^"]*?)"', response)
        return post_url_list, end_cursor

