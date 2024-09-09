import json
import re
from jsonpath_ng import parse

from SocialMediaScraper.models import YtbPostListItem
from SocialMediaScraper.utils import requests_with_retry
from SocialMediaScraper.youtube import HEADERS, CONTEXT


class YtbPostList:
    def __init__(self, cookies=None, proxies=None, user_agent=None, post_num=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS.copy()
        if user_agent:
            self.headers.update({'user-agent': user_agent})
        self.proxies = proxies
        self.item_list = []
        self.post_num = post_num

    def post_list(self, user_id=None, continuation=None):
        if user_id and not continuation:
            response = requests_with_retry.get(f'https://www.youtube.com/{user_id}/videos', cookies=self.cookies,
                                               headers=self.headers, proxies=self.proxies).text
            json_data = re.findall("var ytInitialData\s*=\s*(.*?)\s*;\s*</script>", response)[0]
        elif continuation:
            params = {
                'prettyPrint': 'false',
            }

            json_data = {
                'context': CONTEXT,
                'continuation': continuation,
            }

            json_data = requests_with_retry.post('https://www.youtube.com/youtubei/v1/browse', params=params,
                                                 cookies=self.cookies, headers=self.headers, json=json_data).text
        else:
            return self.item_list

        data = json.loads(json_data)
        _continuation = parse('$..continuationCommand').find(data)
        continuation = _continuation[0].value['token'] if _continuation else None
        print('cursor', continuation)
        post_list = parse('$..videoRenderer').find(data)
        for post in post_list:
            post_value = post.value
            item = YtbPostListItem()
            item.title = post_value['title']['runs'][0]['text']
            item.video_id = post_value['videoId']
            item.url = f'https://www.youtube.com/watch?v={post_value["videoId"]}'
            item.publish_time = post_value['publishedTimeText']['simpleText']

            item.view_count = re.findall("([\d,]+)", post_value['viewCountText']['simpleText'])[0].replace(',', '')
            item.view_count = int(item.view_count)
            item.video_cover_image = post_value['thumbnail']['thumbnails'][0]['url']
            _duration = post_value['lengthText']['simpleText']
            parts = _duration.split(':')
            if len(parts) == 2:  # 格式为 'm:s'
                minutes, seconds = map(int, parts)
                item.duration = minutes * 60 + seconds
            elif len(parts) == 3:  # 格式为 'h:m:s'
                hours, minutes, seconds = map(int, parts)
                item.duration = hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError('Invalid duration format')

            print(item.__dict__)
            self.item_list.append(item.__dict__)
        if self.post_num and self.post_num > len(self.item_list) and continuation:
            self.post_list(continuation=continuation)
        return self.item_list


if __name__ == '__main__':
    ytb_post_list = YtbPostList(post_num=100)
    ytb_post_list.post_list('@Springinglee')
