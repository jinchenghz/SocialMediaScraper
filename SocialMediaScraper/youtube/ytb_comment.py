import json
import re
import requests
from jsonpath_ng import parser
from SocialMediaScraper.models import YtbCommentItem
from SocialMediaScraper.youtube import CONTEXT, HEADERS


class YtbComment:
    def __init__(self, cookies=None, comment_num=0, proxies=None):
        self.cookies = cookies
        self.headers = HEADERS.copy()
        self.comment_list = []
        self.comment_num = comment_num
        self.proxies = proxies

    def get_comment_continuation(self, video_id):
        if video_id.startswith('http'):
            video_id = re.findall('v=(.*?)[&]*', video_id)[0]

        params = {
            'v': video_id,
        }

        response = requests.get('https://www.youtube.com/watch', params=params, cookies=self.cookies,
                                proxies=self.proxies, headers=self.headers).text
        json_data = re.findall("var ytInitialData\s*=\s*(.*?)\s*;\s*</script>", response)[0]
        # print(json_data)
        data = json.loads(json_data)
        subMenus = parser.parse('$..subMenuItems').find(data)[0].value
        for subMenu in subMenus:
            if subMenu.get('title') == "Top comments":
                return parser.parse('..token').find(subMenu).value

        noCookie_data = parser.parse("$..itemSectionRenderer").find(data)
        for d in noCookie_data:
            d_value = d.value
            if d_value.get("targetId") == "comments-section":
                return parser.parse("$..token").find(d_value)[0].value

    def get_comments_data(self, continuation=None, video_id=None):
        if continuation is None and video_id is None:
            raise Exception("video_id or continuation is required")
        if continuation is None:
            continuation = self.get_comment_continuation(video_id)
        params = {
            'prettyPrint': 'false',
        }

        json_data = {
            'context': CONTEXT,
            'continuation': continuation,
        }

        response = requests.post('https://www.youtube.com/youtubei/v1/next', params=params, cookies=self.cookies,
                                 headers=self.headers, json=json_data, proxies=self.proxies).text
        # print(response)
        data = json.loads(response)
        commentEntityPayload = parser.parse("$..commentEntityPayload").find(data)
        for payload in commentEntityPayload:
            comment_data = payload.value
            item = YtbCommentItem()
            item.comment_id = comment_data['properties']['commentId']
            item.comment_content = comment_data["properties"]['content']['content']
            item.comment_time = comment_data["properties"]['publishedTime']
            item.comment_like_count = comment_data['toolbar']['likeCountLiked']
            item.comment_replay_count = comment_data['toolbar']['replyCount']
            item.comment_user_name = comment_data['author']['displayName']
            item.comment_user_id = comment_data['author']['displayName']
            item.comment_user_avatar = comment_data['author']['avatarThumbnailUrl']
            item.comment_user_url = 'https://www.youtube.com/' + comment_data['author']['displayName']
            print(item.__dict__)
            self.comment_list.append(item.__dict__)
        cursor = parser.parse("$..continuationCommand").find(data)[-1].value['token']
        if cursor and len(self.comment_list) < self.comment_num:
            self.get_comments_data(cursor)

        return self.comment_list
