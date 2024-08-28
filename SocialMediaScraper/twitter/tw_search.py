import json
from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.utils import requests_with_retry


class TwSearch:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({"x-csrf-token": cookies.get("ct0")})
        self.cursor = None
        self.post_list = []

    def twitter_post_search(self, keyword, post_num=30, cursor=None):
        params = {
            'variables': '{"rawQuery":"%s","count":%d,"querySource":"typed_query","product":"Top","cursor":"%s"}' % (
                keyword, post_num, cursor),
            'features': '{"rweb_tipjar_consumption_enabled":true,'
                        '"responsive_web_graphql_exclude_directive_enabled":true,'
                        '"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,'
                        '"responsive_web_graphql_timeline_navigation_enabled":true,'
                        '"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,'
                        '"communities_web_enable_tweet_community_results_fetch":true,'
                        '"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,'
                        '"tweetypie_unmention_optimization_enabled":true,'
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
        }

        data = requests_with_retry.get('https://twitter.com/i/api/graphql/TQmyZ_haUqANuyBcFBLkUw/SearchTimeline',
                                       proxies=self.proxies, params=params, cookies=self.cookies,
                                       headers=self.headers).text
        data = json.loads(data)
        if 'Rate limit exceeded' in str(data):
            raise Exception("twitter账号异常：搜索次数超过限制")
        entries = data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][0]['entries']
        for entry in entries:
            itemContent = entry['content'].get('itemContent')
            if not (itemContent and itemContent.get('tweet_results')):
                continue
            try:
                legacy = itemContent['tweet_results']['result']['legacy']
            except:
                continue
            post_id = legacy['id_str']

            content = entry['content']
            itemContent = content['itemContent']
            tweet_results = itemContent['tweet_results']['result']
            user_results = tweet_results['core']['user_results']['result']

            post_info = dict()
            post_info['user_pic'] = user_results['legacy']['profile_image_url_https']
            post_info['user_id'] = user_results['rest_id']
            post_info['user_name'] = user_results['legacy']['name']
            post_info['user_screen_name'] = user_results['legacy']['screen_name']
            post_info['user_followers_count'] = user_results['legacy'].get('followers_count', 0)
            post_info['user_friends_count'] = user_results['legacy'].get('friends_count', 0)
            post_info['user_post_count'] = user_results['legacy'].get('statuses_count', 0)

            post_info['post_id'] = post_id
            post_info['text'] = tweet_results['legacy']['full_text']
            post_info['create_time'] = tweet_results['legacy']['created_at']
            post_info['like_count'] = tweet_results['legacy']['favorite_count']
            post_info['comments_count'] = tweet_results['legacy']['reply_count']
            quote_count = tweet_results['legacy']['quote_count']
            retweet_count = tweet_results['legacy']['retweet_count']
            post_info['forwarding_count'] = quote_count + retweet_count
            post_info['bookmark_count'] = str(tweet_results['legacy']['bookmark_count'])
            post_info['views_count'] = str(tweet_results['views'].get('count', 0))
            try:
                post_info['type'] = tweet_results['legacy']['entities']['media'][0]['type']
            except:
                post_info['type'] = ''
            post_info['url'] = f"https://twitter.com/{user_results['legacy']['screen_name']}/status/{post_id}"

            media_data = tweet_results['legacy']['entities'].get('media', [])
            image_list = []
            video_list = []
            for m in media_data:
                if m.get('type') == 'photo':
                    image_list.append(m['media_url_https'])
                elif m.get('type') == 'video':
                    video_list.append(m['video_info']['variants'][-1]['url'])

            post_info['image_list'] = image_list if image_list else None
            post_info['video_url'] = video_list[0] if video_list else None

            self.post_list.append(post_info)
        try:
            end_entry = data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][-1]['entry']
        except:
            end_entry = entries[-1]
        end_cursor = None
        if end_entry['content']['cursorType'] == 'Bottom':
            end_cursor = end_entry['content']['value']
        if end_entry and len(self.post_list) < post_num:
            self.twitter_post_search(keyword, post_num=post_num, cursor=end_cursor)

        return self.post_list
