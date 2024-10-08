import json
from datetime import datetime

from SocialMediaScraper.models import TwPostItem
from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.utils import requests_with_retry


class TwPost:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies
        self.proxies = proxies
        self.headers = HEADERS.copy()
        self.headers.update({"x-csrf-token": cookies.get("ct0")})
        self.cursor = None

    def tw_post_detail(self, post_url):
        if not post_url.startswith('https://twitter.com/'):
            post_id = post_url.split('/')[-1]
        else:
            post_id = post_url
        variables = {"focalTweetId": post_id, "with_rux_injections": False, "includePromotedContent": True,
                     "withCommunity": True, "withQuickPromoteEligibilityTweetFields": True,
                     "withBirdwatchNotes": True,
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
        if response.status_code != 200:
            raise Exception('账号异常')
        parse_data = json.loads(response.text)
        if 'errors' in parse_data:
            raise Exception('账号异常')
        threaded_conversation_with_injections_v2 = parse_data['data'][
            'threaded_conversation_with_injections_v2']
        instructions = threaded_conversation_with_injections_v2['instructions']
        post_info = TwPostItem()
        for instruction in instructions:
            if instruction['type'] == 'TimelineAddEntries':
                entries = instruction['entries']
                for entry in entries:
                    entryId = entry['entryId']
                    if entryId == f'tweet-{post_id}':
                        content = entry['content']
                        tweet_results = content['itemContent']['tweet_results']['result']
                        user_results = tweet_results['core']['user_results']['result']
                        screen_name = user_results['legacy']['screen_name']
                        post_info.post_id = post_id
                        post_info.content = tweet_results['legacy']['full_text']
                        post_info.publish_time = int(datetime.strptime(tweet_results['legacy']['created_at'],
                                                                       '%a %b %d %H:%M:%S %z %Y').timestamp() * 1000)
                        post_info.favorite_count = tweet_results['legacy']['favorite_count']
                        post_info.reply_count = tweet_results['legacy']['reply_count']
                        post_info.retweet_count = (tweet_results['legacy']['quote_count'] +
                                                   tweet_results['legacy']['retweet_count'])
                        post_info.bookmark_count = tweet_results['legacy']['bookmark_count']
                        post_info.views_count = tweet_results['views'].get(
                            'count') if 'retweeted_status_result' not in tweet_results['legacy'].keys() else \
                            tweet_results['legacy']['retweeted_status_result']['result']['views'].get('count')
                        try:
                            post_info.type = tweet_results['legacy']['entities']['media'][0]['type']
                        except:
                            post_info.type = None
                        post_info.post_url = f'https://twitter.com/{screen_name}/status/{post_id}'

                        # 抓取视频以及图片
                        media_data = tweet_results['legacy']['entities'].get('media', [])
                        image_list = []
                        video_list = []
                        video_cover_image_list = []
                        video_duration_list = []
                        for m in media_data:
                            if m.get('type') == 'photo':
                                image_list.append(m['media_url_https'])
                            elif m.get('type') == 'video':
                                video_list.append(m['video_info']['variants'][-1]['url'])
                                video_cover_image_list.append(m.get("media_url_https"))
                                video_duration_list.append(int(m['video_info'].get('duration_millis') / 1000))
                        post_info.image_list = image_list if image_list else None
                        post_info.video_url_list = video_list[0] if video_list else None
                        post_info.video_cover_image_list = video_cover_image_list if video_cover_image_list else None
                        post_info.video_duration_list = video_duration_list if video_duration_list else None
        print(post_info.__dict__)
        return post_info.__dict__

# if __name__ == '__main__':
#     print(TwPost(cookies).tw_post_detail('https://x.com/MichelBarnier/status/1672150497443172352'))
