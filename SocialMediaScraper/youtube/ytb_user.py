import json
import re

from SocialMediaScraper.models import YtbUserItem
from SocialMediaScraper.utils import requests_with_retry
from SocialMediaScraper.youtube import HEADERS, CONTEXT


class YtbUser:
    def __init__(self, cookies=None, proxies=None, user_agent=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS.copy()
        self.headers.update({'accept-language': 'en-US;'})
        if user_agent:
            self.headers.update({'user-agent': user_agent})
        self.proxies = proxies

    def ytb_user(self, user_id):
        response = requests_with_retry.get(f'https://www.youtube.com/{user_id}', cookies=self.cookies,
                                           headers=self.headers, proxies=self.proxies).text
        item = YtbUserItem()
        item.user_name = re.findall('"channelMetadataRenderer":\{"title":"([^"]*?)"', response)[0]
        item.user_id = user_id
        item.user_url = f'https://www.youtube.com/{user_id}'
        item.description = \
            re.findall('"channelMetadataRenderer":\{"title":"[^"]*?","description":"([^"]*?)"', response)[
                0].strip()
        item.avatar = re.findall('<link itemprop="thumbnailUrl" href="([^"]*?)">', response)[0]
        item.video_count = re.findall('"content":"([^ ]*?) videos"', response)[0]
        # try:
        token = re.findall(
            '"continuationCommand":\s*\{"token":\s*"([^"]*?)",\s*"request":\s*"CONTINUATION_REQUEST_TYPE_BROWSE"',
            response)[-1]
        user_data = self.get_user_data(token)
        item.video_count = int(re.findall("([^ ]*?) videos", user_data['videoCountText'])[0].replace(',', ''))
        item.view_count = int(re.findall("([^ ]*?) views", user_data['viewCountText'])[0].replace(',', ''))
        item.follower_count = re.findall("([^ ]*?) subscribers", user_data['subscriberCountText'])[0].replace(',',
                                                                                                              '')
        if 'K' in item.follower_count:
            item.follower_count = int(float(item.follower_count.replace('K', '')) * 1000)
        elif 'M' in item.follower_count:
            item.follower_count = int(float(item.follower_count.replace('M', '')) * 1000000)
        elif 'B' in item.follower_count:
            item.follower_count = int(float(item.follower_count.replace('B', '')) * 1000000000)
        # except:
        #     item['video_count'] = re.findall('"content":"([^ ]*?) videos"', response)[0]
        #     item['view_count'] = None
        print(item.__dict__)
        return item.__dict__

    def get_user_data(self, token):
        params = {
            'prettyPrint': 'false',
        }

        json_data = {
            'context': CONTEXT,
            'continuation': f'{token}',
        }

        response = requests_with_retry.post(
            'https://www.youtube.com/youtubei/v1/browse', params=params, cookies=self.cookies, headers=HEADERS,
            proxies=self.proxies,
            json=json_data).json()
        return response['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems'][0][
            'aboutChannelRenderer']['metadata']['aboutChannelViewModel']


if __name__ == '__main__':
    ytb_user = YtbUser()
    print(ytb_user.ytb_user('@Chenyifaer288'))
