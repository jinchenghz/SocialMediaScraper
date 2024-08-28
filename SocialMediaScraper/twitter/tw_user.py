import json

from SocialMediaScraper.twitter import HEADERS
from SocialMediaScraper.utils import requests_with_retry


def twitter_user_info(user_name, cookie,proxies):
    headers = HEADERS.copy().update({"x-csrf-token":cookie.get("ct0")})
    headers.update({"x-csrf-token":cookie.get("ct0")})
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
                                       params=params, cookies=cookie, headers=headers,proxies=proxies)
    if response.status_code == 200:
        userInfo = dict()
        user_info_data = json.loads(response.text)
        result = user_info_data['data']['user']['result']

        userInfo['avatar'] = result['legacy']['profile_banner_url']
        userInfo['user_name'] = result['legacy']['name']
        userInfo['favourites_count'] = result['legacy']['favourites_count']
        userInfo['followers'] = result['legacy']['followers_count']
        userInfo['join_time'] = result['legacy']['created_at']
        userInfo['friend_count'] = result['legacy']['friends_count']
        userInfo['location'] = result['legacy']['location']
        userInfo['user_id'] = result['rest_id']

        userInfo['screen_name'] = result['legacy']['screen_name']
        userInfo['listed_count'] = result['legacy']['listed_count']
        userInfo['media_count'] = result['legacy']['media_count']
        userInfo['statuses_count'] = result['legacy']['statuses_count']
        userInfo['birthdate'] = result['legacy_extended_profile']['birthdate']

        # print(userInfo)
        return userInfo
    else:
        raise Exception("get user info error")
