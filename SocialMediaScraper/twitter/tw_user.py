import json
from datetime import datetime

from SocialMediaScraper.models import TwUserItem
from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.utils import requests_with_retry


def twitter_user_info(user_name, cookies, proxies=None):
    headers = HEADERS.copy()
    headers.update({"x-csrf-token": cookies.get("ct0")})
    variables = {"screen_name": user_name, "withSafetyModeUserFields": True}
    features = {"hidden_profile_likes_enabled": True, "hidden_profile_subscriptions_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True, "verified_phone_label_enabled": True,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True, "responsive_web_twitter_article_notes_tab_enabled": True,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True}

    params = {
        'variables': json.dumps(variables),
        'features': json.dumps(features),
        'fieldToggles': '{"withAuxiliaryUserLabels":false}',
    }

    response = requests_with_retry.get('https://twitter.com/i/api/graphql/k5XapwcSikNsEsILW5FvgA/UserByScreenName',
                                       params=params, cookies=cookies, headers=headers, proxies=proxies)
    if response.status_code == 200:
        userInfo = TwUserItem()
        user_info_data = json.loads(response.text)
        result = user_info_data['data']['user']['result']

        userInfo.avatar = result['legacy']['profile_image_url_https']
        userInfo.user_name = result['legacy']['name']
        userInfo.favourites_count = result['legacy']['favourites_count']
        userInfo.followers_count = result['legacy']['followers_count']
        userInfo.join_time = result['legacy']['created_at']
        parsed_date = datetime.strptime(userInfo.join_time, '%a %b %d %H:%M:%S %z %Y')
        userInfo.join_time = int(parsed_date.timestamp() * 1000)
        userInfo.friends_count = result['legacy']['friends_count']
        userInfo.location = result['legacy']['location']
        userInfo.user_id = result['rest_id']
        userInfo.subscriptions_count = result['creator_subscriptions_count']
        userInfo.screen_name = result['legacy']['screen_name']
        userInfo.listed_count = result['legacy']['listed_count']
        userInfo.media_count = result['legacy']['media_count']
        userInfo.statuses_count = result['legacy']['statuses_count']
        userInfo.birthdate = result['legacy_extended_profile'].get('birthdate')
        print(userInfo.__dict__)
        return userInfo.__dict__
    else:
        raise Exception("get user info error")

# if __name__ == '__main__':
#     print(twitter_user_info('elonmusk', cookies=cookies))
