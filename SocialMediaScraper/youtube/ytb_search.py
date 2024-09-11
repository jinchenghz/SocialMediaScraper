import json
import re
import time
from pprint import pprint
import requests
from SocialMediaScraper.models import YtbPostSearchItem
from SocialMediaScraper.utils import requests_with_retry
from SocialMediaScraper.youtube import HEADERS


class YTBSearch:
    def __init__(self, cookies=None, post_num=0,proxies=None, user_agent=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS.copy()
        if user_agent:
            self.headers.update({'user-agent': user_agent})
        self.proxies = proxies
        self.post_list = []
        self.post_num = post_num

    def parse_video_data(self, videoRenderer):
        # try:
        item = YtbPostSearchItem()
        item.title = videoRenderer['title']['runs'][0]['text']
        item.post_id = videoRenderer['videoId']
        item.image_list = [videoRenderer['thumbnail']['thumbnails'][-1]['url']]
        try:
            item.view_count = int(
                videoRenderer['viewCountText']['simpleText'].replace('次观看', '').replace(',', ''))
        except:
            item.view_count = 0
        item.content = ''.join([i['text'] for i in videoRenderer['detailedMetadataSnippets'][0]['snippetText']
        ['runs']]) if videoRenderer.get('detailedMetadataSnippets') else ''
        item.post_url = 'https://www.youtube.com' + videoRenderer['inlinePlaybackEndpoint']['commandMetadata'][
            'webCommandMetadata']['url']

        # 获取视频封面
        item.video_cover_image = videoRenderer['thumbnail']['thumbnails'][-1]['url']
        duration = videoRenderer['lengthText']['simpleText']
        time_list = duration.split(':')
        if len(time_list) == 2:
            item.duration = int(time_list[0]) * 60 + int(time_list[1])
        elif len(time_list) == 3:
            item.duration = int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])
        else:
            raise Exception('时间格式错误')

        item.create_time = videoRenderer['publishedTimeText']['simpleText']
        if videoRenderer.get('richThumbnail'):
            item.user_avatar = \
            videoRenderer['richThumbnail']['movingThumbnailRenderer']["movingThumbnailDetails"][
                'thumbnails'][0]['url']
        else:
            item.user_avatar = videoRenderer['thumbnail']['thumbnails'][-1]['url']
        item.user_name = videoRenderer['longBylineText']['runs'][0]['text']
        item.user_url = 'https://www.youtube.com' + videoRenderer['longBylineText']['runs'][0][
            'navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
        item.user_id = videoRenderer['longBylineText']['runs'][0]['navigationEndpoint']['commandMetadata'][
            'webCommandMetadata']['url']
        if item.user_id.startswith('/'):
            item.user_id = item.user_id[1:]
        # 获取用户粉丝数
        item.followers = self.youtube_user_info_followers(item.user_id)
        print(item.__dict__)
        return item.__dict__
        # except Exception as e:
        #     print(e)
        #     print('error', videoRenderer)
        #     return None

    def youtube_post_search(self, keyword, end_cursor=None):
        params = {
            'prettyPrint': 'false',
        }
        json_data = {
            'context': {
                'client': {
                    'hl': 'zh-CN',
                    'gl': 'US',
                    'remoteHost': '101.44.80.206',
                    'deviceMake': '',
                    'deviceModel': '',
                    'visitorData': 'CgswU3k0Wmw4N0RuQSiwhvm0BjIKCgJDThIEGgAgJg%3D%3D',
                    'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36,gzip(gfe)',
                    'clientName': 'WEB',
                    'clientVersion': '2.20240702.09.00',
                    'osName': 'Windows',
                    'osVersion': '10.0',
                    'originalUrl': 'https://www.youtube.com/results?search_query=china',
                    'screenPixelDensity': 2,
                    'platform': 'DESKTOP',
                    'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                    'configInfo': {
                        'appInstallData': 'CLCG-bQGEPGcsAUQ2cmvBRDl9LAFEKaasAUQjcywBRChnbEFENWw_xIQo-2wBRC3k7EFEIjjrwUQ9quwBRDJ5rAFEOPRsAUQ-vCwBRCmkrEFEJT-sAUQ1ouxBRC9irAFEO_NsAUQ8Y6xBRDK-bAFEI_EsAUQt--vBRDf9bAFEIvPsAUQ4tSuBRCOlLEFEKy8_xIQgIuxBRD3sf8SEN3o_hIQg7n_EhDT4a8FEM-osAUQooGwBRCx3LAFEJCSsQUQzN-uBRCw7rAFENaPsQUQ3Y6xBRD0q7AFENbdsAUQnaawBRDr6P4SEKWWsQUQieiuBRD-iLEFELr4sAUQxIyxBRDJ17AFEKrYsAUQt-r-EhDbr68FEOuTrgUQ1YiwBRDqw68FEMn3rwUQl4OxBRC9mbAFENShrwUQuJaxBRDY3bAFEI7asAUQlpWwBRCUibEFEJ3QsAUQ7qKvBRComrAFENv-tyIQppOxBRClwv4SEJrwrwUQqJKxBRDEkrEFEJSVsQUQqJOxBRCIh7AFEPyFsAUQtbH_EhDX6a8FEND6sAUQ0I2wBRDN17AFEN-8_xIQvbauBRDYhLEFEOHssAUQ65mxBRCMlLEFENaUsQUQ4b3_EhCkkbEFKihDQU1TR0JVVHBiMndETnprQm9PejlBdm9zUVQyN1FhVWdnSWRCdz09',
                    },
                    'screenDensityFloat': 1.5,
                    'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                    'timeZone': 'Asia/Shanghai',
                    'browserName': 'Chrome',
                    'browserVersion': '126.0.0.0',
                    'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'deviceExperimentId': 'ChxOek01TkRReU1UVXhNelEwTWpBMU5qZzVNZz09ELCG-bQGGLCG-bQG',
                    'screenWidthPoints': 1707,
                    'screenHeightPoints': 505,
                    'utcOffsetMinutes': 480,
                    'memoryTotalKbytes': '8000000',
                    'mainAppWebInfo': {
                        'graftUrl': '/results?search_query=china',
                        'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                        'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                        'isWebNativeShareAvailable': True,
                    },
                },
                'user': {
                    'lockedSafetyMode': False,
                },
                'request': {
                    'useSsl': True,
                    'internalExperimentFlags': [],
                    'consistencyTokenJars': [],
                },
                'clickTracking': {
                    'clickTrackingParams': 'CBMQ7VAiEwiuw-Kblo2HAxU29jgGHXXsDbM=',
                },
                'adSignalsInfo': {
                    'params': [
                        {
                            'key': 'dt',
                            'value': f'{int(time.time() * 1000)}',
                        },
                        {
                            'key': 'flash',
                            'value': '0',
                        },
                        {
                            'key': 'frm',
                            'value': '0',
                        },
                        {
                            'key': 'u_tz',
                            'value': '480',
                        },
                        {
                            'key': 'u_his',
                            'value': '3',
                        },
                        {
                            'key': 'u_h',
                            'value': '960',
                        },
                        {
                            'key': 'u_w',
                            'value': '1707',
                        },
                        {
                            'key': 'u_ah',
                            'value': '912',
                        },
                        {
                            'key': 'u_aw',
                            'value': '1707',
                        },
                        {
                            'key': 'u_cd',
                            'value': '24',
                        },
                        {
                            'key': 'bc',
                            'value': '31',
                        },
                        {
                            'key': 'bih',
                            'value': '505',
                        },
                        {
                            'key': 'biw',
                            'value': '1691',
                        },
                        {
                            'key': 'brdim',
                            'value': '0,0,0,0,1707,0,1707,912,1707,505',
                        },
                        {
                            'key': 'vis',
                            'value': '1',
                        },
                        {
                            'key': 'wgl',
                            'value': 'true',
                        },
                        {
                            'key': 'ca_type',
                            'value': 'image',
                        },
                    ],
                    'bid': 'ANyPxKp2snaRCyVCBPccuVpHoTYFZDQPq_cvzczJ2BVz4VdUgZFhlkYzp-BT4kHYegVhY1vwVzmj2GZC5lV338M8JAmnNyB45A',
                },
            },
            'query': keyword,
            'continuation': end_cursor,
        }
        response = requests.post(
            'https://www.youtube.com/youtubei/v1/search', params=params, headers=self.headers, json=json_data,
            cookies=self.cookies, proxies=self.proxies).text
        # print(response)
        data = json.loads(response)
        if data.get("contents"):
            video_list = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                'contents'][0]['itemSectionRenderer']['contents']
            end_cursor = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                'contents'][-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
        else:
            video_list = data['onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems'][0][
                'itemSectionRenderer']['contents']
            end_cursor = data['onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems'][1][
                'continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
        print('end_cursor', end_cursor)
        for video in video_list:
            if not video.get("videoRenderer") and video.get('shelfRenderer'):
                v_list = video["shelfRenderer"]['content']['verticalListRenderer']['items']
                for v in v_list:
                    if len(self.post_list) >= self.post_num:
                        return self.post_list
                    videoRenderer = v['videoRenderer']
                    post_item = self.parse_video_data(videoRenderer)
                    if post_item:
                        self.post_list.append(post_item)
            elif video.get("videoRenderer"):
                if len(self.post_list) >= self.post_num:
                    return self.post_list
                videoRenderer = video['videoRenderer']
                post_item = self.parse_video_data(videoRenderer)
                if post_item:
                    self.post_list.append(post_item)

        if len(self.post_list) < self.post_num and end_cursor:
            self.youtube_post_search(keyword, end_cursor)

        return self.post_list

    def youtube_user_info_followers(self, user_id):
        print(f'https://www.youtube.com/{user_id}')
        response = requests_with_retry.get(f'https://www.youtube.com/{user_id}', cookies=self.cookies,
                                           headers=self.headers, proxies=self.proxies).text

        followers = re.findall('"content":\s*"([^"]*?) subscribers"', response)
        if not followers:
            followers = re.findall('"content":\s*"([^"]*?)位订阅者"', response)

        return followers[0]
