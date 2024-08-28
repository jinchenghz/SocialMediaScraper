import json
from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.utils import requests_with_retry


class TWComment:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({"x-csrf-token": cookies.get("ct0")})
        self.cursor = None
        self.comment_list = []

    def get_comment_list(self, post_id, comment_count):
        variables = {"focalTweetId": post_id, "cursor": self.cursor, "referrer": "tweet",
                     "with_rux_injections": False, "includePromotedContent": True, "withCommunity": True,
                     "withQuickPromoteEligibilityTweetFields": True, "withBirdwatchNotes": True,
                     "withVoice": True, "withV2Timeline": True}
        params = {
            'variables': json.dumps(variables),
            'features': '{"responsive_web_graphql_exclude_directive_enabled":true,'
                        '"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,'
                        '"responsive_web_graphql_timeline_navigation_enabled":true,'
                        '"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,'
                        '"c9s_tweet_anatomy_moderator_badge_enabled":true,'
                        '"tweetypie_unmention_optimization_enabled":true,'
                        '"responsive_web_edit_tweet_api_enabled":true,'
                        '"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,'
                        '"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,'
                        '"responsive_web_twitter_article_tweet_consumption_enabled":true,'
                        '"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,'
                        '"standardized_nudges_misinfo":true,'
                        '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,'
                        '"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,'
                        '"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            'fieldToggles': '{"withArticleRichContentState":true}',
        }
        response = requests_with_retry.get(
            'https://twitter.com/i/api/graphql/ZkD-1KkxjcrLKp60DPY_dQ/TweetDetail', params=params,
            cookies=self.cookies, headers=self.headers)
        if response.status_code == 200:
            raise Exception('Twitter api error')
        parse_data = json.loads(response.text)
        if 'errors' in parse_data:
            raise Exception('Twitter api error')
        threaded_conversation_with_injections_v2 = parse_data['data']['threaded_conversation_with_injections_v2']
        instructions = threaded_conversation_with_injections_v2['instructions']
        for instruction in instructions:
            if instruction['type'] == 'TimelineAddEntries':
                for entry in instruction['entries']:
                    entryId = entry['entryId']
                    if 'conversationthread' in entryId:
                        comment_info = {}
                        comment_itemContent = entry['content']['items'][0]['item']['itemContent']
                        comment_tweet_results = comment_itemContent['tweet_results']['result']
                        comment_user_results = comment_tweet_results['core']['user_results']['result']

                        comment_info['comment_id'] = comment_tweet_results['legacy'].get('id_str')
                        comment_info['screen_name'] = comment_user_results['legacy']['screen_name']
                        comment_info['user_name'] = comment_user_results['legacy']['name']
                        comment_info['avatar'] = comment_user_results['legacy']['profile_image_url_https']
                        comment_info['user_id'] = comment_user_results['rest_id']
                        comment_info['created_time'] = comment_tweet_results['legacy']['created_at']
                        comment_info['comment_content'] = comment_tweet_results['legacy']['full_text']
                        comment_info['like_num'] = comment_tweet_results['legacy']['favorite_count']

                        self.comment_list.append(comment_info)
                    if 'cursor-bottom' in entryId:
                        self.cursor = entry['content']
        if self.cursor and len(self.comment_list) <= comment_count:
            self.get_comment_list(post_id, comment_count)

        return self.comment_list
