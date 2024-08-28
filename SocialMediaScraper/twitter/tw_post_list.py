import json

from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.twitter.tw_user import twitter_user_info
from SocialMediaScraper.utils import requests_with_retry


class TWPostList:
    def __init__(self, cookies, proxies):
        self.cookies = cookies
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({"x-csrf-token": cookies.get("ct0")})
        self.cursor = None
        self.post_list = []
        self.user_id = None

    def get_post_list(self, screen_name, post_num, cursor=None):
        if not self.user_id:
            self.user_id = twitter_user_info(screen_name, self.cookies, self.proxies).get("user_id")
        features = {"responsive_web_graphql_exclude_directive_enabled": True, "verified_phone_label_enabled": False,
                    "creator_subscriptions_tweet_preview_api_enabled": True,
                    "responsive_web_graphql_timeline_navigation_enabled": True,
                    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                    "c9s_tweet_anatomy_moderator_badge_enabled": True, "tweetypie_unmention_optimization_enabled": True,
                    "responsive_web_edit_tweet_api_enabled": True,
                    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                    "view_counts_everywhere_api_enabled": True, "longform_notetweets_consumption_enabled": True,
                    "responsive_web_twitter_article_tweet_consumption_enabled": True,
                    "tweet_awards_web_tipping_enabled": False, "freedom_of_speech_not_reach_fetch_enabled": True,
                    "standardized_nudges_misinfo": True,
                    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                    "rweb_video_timestamps_enabled": True, "longform_notetweets_rich_text_read_enabled": True,
                    "longform_notetweets_inline_media_enabled": True, "responsive_web_enhance_cards_enabled": False}
        variables = {"userId": self.user_id, "count": 40, "cursor": cursor, "includePromotedContent": True,
                     "withQuickPromoteEligibilityTweetFields": True, "withVoice": True, "withV2Timeline": True}

        params = {
            'variables': json.dumps(variables),
            'features': json.dumps(features),
        }

        response = requests_with_retry.get('https://twitter.com/i/api/graphql/eS7LO5Jy3xgmd3dbL044EA/UserTweets',
                                           headers=self.headers,params=params, cookies=self.cookies)
        if not response.status_code == 200:
            print(response.text)
            raise Exception(f'Twitter post list request failed with status code {response.status_code}')
        data = json.loads(response.text)
        print(data)
        instructions = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
        for instruction in instructions:
            if instruction['type'] == 'instructions':
                entries = instruction['entries']
                for entry in entries:
                    entryId = entry['entryId']
                    if 'tweet' in entryId:
                        sortIndex = entry['sortIndex']
                        url = f'https://twitter.com/{screen_name}/status/{sortIndex}'
                        self.post_list.append(url)
                    if 'bottom' in entryId:
                        self.cursor = entry['content']
        if self.cursor and len(self.post_list) < post_num:
            self.get_post_list(screen_name, post_num, self.cursor)
