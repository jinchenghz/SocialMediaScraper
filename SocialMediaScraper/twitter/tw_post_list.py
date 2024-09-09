import json
import re
from datetime import datetime
from jsonpath_ng import parse

from SocialMediaScraper.models import TwPostListItem
from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.twitter.tw_user import twitter_user_info
from SocialMediaScraper.utils import requests_with_retry


class TwPostList:
    def __init__(self, cookies, post_num=10, proxies=None):
        self.cookies = cookies
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({"x-csrf-token": cookies.get("ct0")})
        self.cursor = None
        self.post_list = []
        self.post_num = post_num

    def tw_post_list(self, userId, cursor=None):
        # 兼容user_name
        if not userId.isdigit():
            userId = twitter_user_info(userId, cookies=self.cookies, proxies=self.proxies).get("user_id")
        if cursor:
            variables = {"userId": f"{userId}", "count": 20, "cursor": f"{cursor}", "includePromotedContent": True,
                         "withQuickPromoteEligibilityTweetFields": True, "withVoice": True, "withV2Timeline": True}

        else:
            variables = {"userId": f"{userId}", "count": 20, "includePromotedContent": True,
                         "withQuickPromoteEligibilityTweetFields": True, "withVoice": True, "withV2Timeline": True}

        params = {
            'variables': json.dumps(variables),
            'features': '{"rweb_tipjar_consumption_enabled":true,'
                        '"responsive_web_graphql_exclude_directive_enabled":true,'
                        '"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,'
                        '"responsive_web_graphql_timeline_navigation_enabled":true,'
                        '"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,'
                        '"communities_web_enable_tweet_community_results_fetch":true,'
                        '"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,'
                        '"responsive_web_edit_tweet_api_enabled":true,'
                        '"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,'
                        '"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,'
                        '"responsive_web_twitter_article_tweet_consumption_enabled":true,'
                        '"tweet_awards_web_tipping_enabled":false,'
                        '"creator_subscriptions_quote_tweet_preview_enabled":false,'
                        '"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,'
                        '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,'
                        '"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,'
                        '"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            'fieldToggles': '{"withArticlePlainText":false}',
        }

        response = requests_with_retry.get(
            'https://x.com/i/api/graphql/E3opETHurmVJflFsUBVuUQ/UserTweets',
            params=params, cookies=self.cookies, headers=self.headers, proxies=self.proxies).text
        data = json.loads(response)
        tweets = parse("$..result").find(data)
        for tweet in tweets:
            tweet = tweet.value
            if 'views' not in tweet.keys():
                continue
            user_name = tweet['core']['user_results']['result']['legacy']['screen_name']
            views = tweet['views'].get('count')
            legacy = tweet['legacy']
            if 'full_text' not in legacy.keys():
                continue
            item = TwPostListItem()
            item.user_id = legacy['user_id_str']
            if item.user_id != str(userId):
                continue
            item.user_name = user_name
            item.views_count = views
            item.content = legacy['full_text']
            item.bookmark_count = legacy['bookmark_count']
            item.favorite_count = legacy['favorite_count']
            item.reply_count = legacy['reply_count']
            item.retweet_count = legacy['retweet_count'] + legacy['quote_count']
            item.post_id = legacy['id_str']
            item.post_url = f"https://twitter.com/{user_name}/status/{item.post_id}"
            parsed_time = datetime.strptime(legacy['created_at'], '%a %b %d %H:%M:%S %z %Y')
            item.publish_time = int(parsed_time.timestamp() * 1000)

            # 抓取视频以及图片
            media_data = legacy['entities'].get('media', [])
            image_list = []
            video_url_list = []
            video_cover_image_list = []
            video_duration_list = []
            for m in media_data:
                if m.get('type') == 'photo':
                    image_list.append(m['media_url_https'])
                elif m.get('type') == 'video':
                    video_url_list.append(m['video_info']['variants'][-1]['url'])
                    video_cover_image_list.append(m.get("media_url_https"))
                    video_duration_list.append(int(m['video_info'].get('duration_millis') / 1000))
            item.image_list = image_list if image_list else None
            item.video_url = video_url_list[0] if video_url_list else None
            item.video_cover_image = video_cover_image_list[
                0] if video_cover_image_list else None
            item.video_duration = video_duration_list[0] if video_duration_list else None

            print(item.__dict__)
            self.post_list.append(item.__dict__)

        cursor = re.findall('"value":\s*"([^"]*?)",\s*"cursorType":\s*"Bottom"', response)[0]
        print("cursor", cursor)
        if cursor and self.post_num > len(self.post_list):
            self.tw_post_list(userId, cursor)


if __name__ == '__main__':
    cookies = {
        'night_mode': '2',
        'g_state': '{"i_l":0}',
        'kdt': 'mvxnlwH9sixk66F7srsCpTQy3bmnHkJBXqq5JkOT',
        'lang': 'en',
        'gt': '1833070446423794075',
        'ads_prefs': '"HBIRAAA="',
        'auth_token': '625329f8b807bdac1cda1b97442e9f61b165c223',
        'guest_id_ads': 'v1%3A172587303033737014',
        'guest_id_marketing': 'v1%3A172587303033737014',
        'guest_id': 'v1%3A172587303033737014',
        'twid': 'u%3D1698901454076227584',
        'ct0': '9fadb013b4530110b552d481f384d811f9bd5ac8d64a8ceb326eb1026cf3a4a7a178b062b57af4c34afeef150f024ef41c8ad96cbbf3f3dfeef54d80bdd0ad1a7a2ee4a9940d9437fed90c710087a511',
        'personalization_id': '"v1_dKobad34izz2II/xJrpJbQ=="',
    }
    TwPostList(cookies, 10).tw_post_list('MarioNawfal')
