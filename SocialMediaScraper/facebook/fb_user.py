import json
import re
from SocialMediaScraper.facebook import HEADERS
from SocialMediaScraper.models import FbUserItem
from SocialMediaScraper.utils import requests_with_retry


class FBUser:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.client_id = self.cookies['c_user']
        self.proxies = proxies

    def fb_user(self, userId):
        if userId.isdigit():
            userId = int(userId)
            params = {
                'id': str(userId),
                'sk': 'about_contact_and_basic_info',
            }
            response = requests_with_retry.get('https://www.facebook.com/profile.php', params=params,
                                               cookies=self.cookies,
                                               proxies=self.proxies, headers=HEADERS).text
            location_params = {
                'id': str(userId),
                'sk': 'about',
            }
            location_response = requests_with_retry.get('https://www.facebook.com/profile.php', params=location_params,
                                                        proxies=self.proxies, cookies=self.cookies,
                                                        headers=HEADERS).text
            url = f'https://www.facebook.com/profile.php?id={userId}'
        else:
            response = requests_with_retry.get(f'https://www.facebook.com/{userId}/about_contact_and_basic_info',
                                               cookies=self.cookies, proxies=self.proxies, headers=HEADERS).text
            location_response = requests_with_retry.get(f'https://www.facebook.com/{userId}/about',
                                                        cookies=self.cookies, proxies=self.proxies,
                                                        headers=HEADERS).text
            url = f'https://www.facebook.com/{userId}'
        if "This content isn't available right now" in response:
            raise Exception('当前页面信息错误')
        item = FbUserItem()
        item.user_url = url
        user_id = re.findall('"userID":\s*"(\d+)"', response)
        item.user_id = user_id[0] if user_id else None
        name = re.findall("<title>([^<]*?)</title>", response)
        item.user_name = name[0] if name else None
        friends = re.findall('"text":\s*"(\d[^"]*?)\sfriends"', response)
        item.friends_count = friends[0] if friends else None
        followers = re.findall('"text":\s*"(\d[^"]*?)\sfollowers"', response)
        item.followers_count = followers[0] if followers else None
        likes = re.findall('"text":\s*"(\d[^"]*?)\slikes"', response)
        item.likes_count = likes[0] if likes else None
        following = re.findall('"text":\s*"(\d[^"]*?)\sfollowing"', response)
        item.following_count = following[0] if following else None
        location = re.findall('"text":\s*"Lives in ([^"]*?)"', location_response)
        item.location = location[0] if location else None
        profile_pic = re.findall('"profilePicLarge":\s*\{\s*"uri":\s*"([^"]*?)"', response)
        item.avatar = profile_pic[0].replace("\\", "") if profile_pic else None
        gender = re.findall('"gender":\s*"([^"]*?)"', response)
        item.gender = gender[0] if gender else None
        birth_year = None
        birth_date = None
        if 'Birth year' in response:
            birth_year = re.findall('dir="auto">(\d{4})<', response)
        if 'Birth date' in response:
            birth_date = re.findall('dir="auto">([^\s]*?\s\d+)<', response)
        if birth_year and birth_date:
            item.birthday = birth_date[0] + ' ,' + birth_year[0]
        elif birth_year:
            item.birthday = birth_year[0]
        else:
            item.birthday = None
        return item.__dict__
