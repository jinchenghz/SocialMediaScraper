import datetime
import json
import os
import re
import subprocess
import time

from SocialMediaScraper.models import YtbVideoItem
from SocialMediaScraper.utils import requests_with_retry
from SocialMediaScraper.youtube import HEADERS, CONTEXT


class YtbPost:
    def __init__(self, cookies=None, proxies=None, user_agent=None):
        self.cookies = cookies if not isinstance(cookies, str) else json.loads(cookies)
        self.headers = HEADERS.copy()
        if user_agent:
            self.headers.update({'user-agent': user_agent})
        self.proxies = proxies

    def ytb_post_detail(self, video_id):
        params = {
            'v': video_id,
        }
        response = requests_with_retry.get('https://www.youtube.com/watch', params=params, cookies=self.cookies,
                                           proxies=self.proxies, headers=self.headers).text
        item = YtbVideoItem()
        avatar_list = re.findall('"videoOwnerRenderer":\s*\{"thumbnail":\s*\{"thumbnails":\s*(\[[^]]*?\])', response)
        item.avatar = json.loads(avatar_list[0])[-1]['url']
        try:
            item.follower_count = re.findall('"subscriberCountText":.*?"simpleText":\s*"([^"]*?)\s*subscribers"\}',
                                             response)[0].replace(',', '')
            if 'K' in item.follower_count:
                item.follower_count = int(float(item.follower_count.replace('K', '')) * 1000)
            elif 'M' in item.follower_count:
                item.follower_count = int(float(item.follower_count.replace('M', '')) * 1000000)
            elif 'B' in item.follower_count:
                item.follower_count = int(float(item.follower_count.replace('B', '')) * 1000000000)
        except:
            item.follower_count = re.findall('"subscriberCountText":.*?"simpleText":\s*"([^"]*?)\s*位订阅者"\}',
                                             response)[0].replace(',', '')
            if '万' in item.follower_count:
                item.follower_count = int(float(item.follower_count.replace('万', '')) * 10000)

        try:
            video_detail = re.findall('"playerMicroformatRenderer"\s*:\s*(\{.*?\})\s*\}', response)
            # print(video_detail)
            video_data = json.loads(video_detail[0])
            if video_detail:
                item.title = video_data['title']['simpleText']
                item.content = video_data['description']['simpleText']
                item.publish_time = int(
                    datetime.datetime.fromisoformat(video_data['publishDate']).timestamp()) * 1000
                item.duration = int(video_data['lengthSeconds'])
                item.view_count = int(video_data['viewCount'])
                item.video_cover_image = video_data['thumbnail']['thumbnails'][0]['url']
                item.user_name = video_data['ownerChannelName']
                item.user_url = video_data['ownerProfileUrl']
                item.user_id = re.findall("(@[^?]*)", item.user_url)[0]
        except:
            item.title = \
                re.findall('"playerOverlayVideoDetailsRenderer":\s*\{\s*"title":\s*\{\s*"simpleText":"([^"]*?)"',
                           response)[
                    0]
            item.content = re.findall('"attributedDescriptionBodyText":\{"content":"([^"]*?)"', response)[0]
            publish_time = re.findall('"dateText":\{"simpleText":"([^"]*?)"}', response)[0]
            try:
                item.publish_time = int(datetime.datetime.strptime(publish_time, "%b %d, %Y").timestamp()) * 1000
            except:
                # 获取当天零点时间戳
                publish_time = datetime.datetime.today().strftime("%Y-%m-%d")
                item.publish_time = int(datetime.datetime.strptime(publish_time, "%Y-%m-%d").timestamp()) * 1000
            _duration = \
                re.findall('"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]*?)"}', response)[
                    0]
            hour = re.findall('(\d+) hours', _duration)
            hour = hour[0] if hour else 0
            minute = re.findall('(\d+) minutes', _duration)
            minute = minute[0] if minute else 0
            second = re.findall('(\d+) seconds', _duration)
            second = second[0] if second else 0
            item.duration = int(hour) * 3600 + int(minute) * 60 + int(second)
            item.view_count = int(
                re.findall('"videoViewCountRenderer":\{"viewCount":\{"simpleText":"([^ ]*?) views"}', response)[
                    0].replace(
                    ",", ""))
            item.video_cover_image = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

            item.user_name = re.findall('"channel":\{"simpleText":"([^"]*?)"}', response)[0]
            item.user_id = re.findall('"commandMetadata":\{"webCommandMetadata":\{"url":"/(@[^"]*?)"', response)[0]
            item.user_url = f"https://www.youtube.com/{item.user_id}"

        item.video_id = video_id
        item.video_url = 'https://www.youtube.com/watch?v=' + video_id

        try:
            item.like_count = int(
                re.findall('"accessibilityText":"like this video along with (.*?) other people"', response)[0].replace(
                    ',',
                    ''))
        except:
            #     与另外 11,080 人一起赞此视频
            item.like_count = int(
                re.findall('"accessibilityText":"与另外 (.*?) 人一起赞此视频"', response)[0].replace(',', ''))

        try:
            comment_token = re.findall(
                '"continuationCommand":\s*\{"token":\s*"([^"]*?)",\s*"request":\s*"CONTINUATION_REQUEST_TYPE_WATCH_NEXT"',
                response)[0]
            item.comment_count = self.get_comment_count(comment_token)
        except:
            item.comment_count = re.findall('"commentCount":\s*\{\s*"simpleText":\s*"([^"]*?)"', response)[0]
            if 'K' in item.comment_count:
                item.comment_count = int(float(item.comment_count.replace('K', '')) * 1000)
            elif 'M' in item.comment_count:
                item.comment_count = int(float(item.comment_count.replace('M', '')) * 1000000)
            elif 'B' in item.comment_count:
                item.comment_count= int(float(item.comment_count.replace('B', '')) * 1000000000)

        print(item.__dict__)
        return item.__dict__

    def get_comment_count(self, comment_token):
        params = {
            'prettyPrint': 'false',
        }

        json_data = {
            'context': CONTEXT,
            'continuation': comment_token,
        }

        response = requests_with_retry.post('https://www.youtube.com/youtubei/v1/next', params=params,
                                            cookies=self.cookies, proxies=self.proxies,
                                            headers=self.headers, json=json_data, timeout=30).json()
        comment = response['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0][
            'commentsHeaderRenderer']['countText']['runs'][0]['text']
        # print(comment)
        return int(comment.replace(',', ''))

    def get_short_video_duration(self, video_id):
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': f'SAPISIDHASH {self.get_authorization()}',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'cookie': 'VISITOR_INFO1_LIVE=0Sy4Zl87DnA; VISITOR_PRIVACY_METADATA=CgJDThIEGgAgJg%3D%3D; PREF=tz=Asia.Shanghai&f4=4000000&hl=en&f5=20000; SID=g.a000mgiTgw-P2ZicjR3x9NA3TZJ6tYmhxrvx95r2wrtxvX4q15gQJnokl3JF2LoVA-aDg6ai3AACgYKAakSARcSFQHGX2MipYWG4UEzBQhJSOW27xcFDRoVAUF8yKriy5gTOwFspcdGOA43_P-R0076; __Secure-1PSID=g.a000mgiTgw-P2ZicjR3x9NA3TZJ6tYmhxrvx95r2wrtxvX4q15gQnabhX_4FUNWTf6_UtaX4AwACgYKAWwSARcSFQHGX2MiKHGaFSeGsn_4GSd3SqLB6xoVAUF8yKrveXrydN-YrqY1NASlIAtR0076; __Secure-3PSID=g.a000mgiTgw-P2ZicjR3x9NA3TZJ6tYmhxrvx95r2wrtxvX4q15gQ24_C4tO2NqQMPcETfhbYlQACgYKAWkSARcSFQHGX2MiKoh30eealDrbFK7oWab9jhoVAUF8yKpCDq5LPPILr8Hwmtq1qDKf0076; HSID=AAyidyobb5qkCkfA3; SSID=AfF3lhl2nXhLdDcYs; APISID=TUQthdYN2-r9P5WV/A5iGX9X87B-RSrCto; SAPISID=jBVVXIeaukfEa6jP/A_aLTGXuLvAc72-Bd; __Secure-1PAPISID=jBVVXIeaukfEa6jP/A_aLTGXuLvAc72-Bd; __Secure-3PAPISID=jBVVXIeaukfEa6jP/A_aLTGXuLvAc72-Bd; LOGIN_INFO=AFmmF2swRAIgcH1dVUGqyhnxFIHGcwN9f_Z5mOleRyvsiufT-A-PBtwCIDSJtavt7OuQKG8M7vu_6AMIra8g8fKfseb1fcfuvM0b:QUQ3MjNmeGVqbF8zMUNOaWR1bDhaRzhYbU5hNHI3ZE5sV2habEVjM2FFT3RTZDdCRmhoTk5qQ1MzMEtraTNySWFaRUhHaTF1Q0xRREEzeGZDWWRxWFczQmxpTlZZM2xYc1QwcWJmNl9lWnpoU1cycm01cUYyOFd1QjNiQnI0R3RMZEJvZ2FMUUFuazl1WGowOHZ0aHA0WDJHbFNTSm91WmtR; YSC=vusrrm7aBpw; SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjQwODA2LjA0X3AwGgJlbiACGgYIgLjVtQY; __Secure-1PSIDTS=sidts-CjEB4E2dkTBOJsjMYxT8Jt2koF4gBF5sPtVgdioIFRIZcf73B_JLXlfPkNhbTUrfkXl4EAA; __Secure-3PSIDTS=sidts-CjEB4E2dkTBOJsjMYxT8Jt2koF4gBF5sPtVgdioIFRIZcf73B_JLXlfPkNhbTUrfkXl4EAA; ST-tladcw=session_logininfo=AFmmF2swRAIgcH1dVUGqyhnxFIHGcwN9f_Z5mOleRyvsiufT-A-PBtwCIDSJtavt7OuQKG8M7vu_6AMIra8g8fKfseb1fcfuvM0b%3AQUQ3MjNmeGVqbF8zMUNOaWR1bDhaRzhYbU5hNHI3ZE5sV2habEVjM2FFT3RTZDdCRmhoTk5qQ1MzMEtraTNySWFaRUhHaTF1Q0xRREEzeGZDWWRxWFczQmxpTlZZM2xYc1QwcWJmNl9lWnpoU1cycm01cUYyOFd1QjNiQnI0R3RMZEJvZ2FMUUFuazl1WGowOHZ0aHA0WDJHbFNTSm91WmtR; SIDCC=AKEyXzV3eHhS52c_b7S6Ioyv9DkaaP_pHBVaDqN8-QWghig8IOPM8kErOeAhzQVBfh_k0bxm; __Secure-1PSIDCC=AKEyXzWXK6j9zDSoaCnDI1XUlkzeCVM7wzH5sJDK2dOrZFt1DpVhq3zRWwtKkQ58pg9uUNwq; __Secure-3PSIDCC=AKEyXzUElJf80FLZ0J7_sGN4jF1FAHxYKdh98gXMpCvmmIiffvMRAwYIVrLHkiQyGg7WOL-DJH0; ST-18r0wzi=endpoint=%7B%22clickTrackingParams%22%3A%22CBwQ7fkGGAAiEwj3m4SM7-aHAxXQWA8CHVL0ADQ%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fshorts%2F5osDwOF9Ztw%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_SHORTS%22%2C%22rootVe%22%3A37414%7D%7D%2C%22reelWatchEndpoint%22%3A%7B%22videoId%22%3A%225osDwOF9Ztw%22%2C%22playerParams%22%3A%228AEByAMTwAT_hoTkudrDmmSiBhUBNuhjh1J5fxqFJylQZaRgpQHBo72qBkNBT0FyQkZ0X2dXSGdwNWwtN3RRd2Fwb1B0QXVOcTNzdF9zbU9NMDBwcE9ZNTYzS19tb2JsNk54OXpvb19vNlg5UlZZ%22%2C%22thumbnail%22%3A%7B%22thumbnails%22%3A%5B%7B%22url%22%3A%22https%3A%2F%2Fi.ytimg.com%2Fvi%2F5osDwOF9Ztw%2Fframe0.jpg%22%2C%22width%22%3A1080%2C%22height%22%3A1920%7D%5D%2C%22isOriginalAspectRatio%22%3Atrue%7D%2C%22overlay%22%3A%7B%22reelPlayerOverlayRenderer%22%3A%7B%22style%22%3A%22REEL_PLAYER_OVERLAY_STYLE_SHORTS%22%2C%22trackingParams%22%3A%22CB0QsLUEIhMI95uEjO_mhwMV0FgPAh1S9AA0%22%2C%22reelPlayerNavigationModel%22%3A%22REEL_PLAYER_NAVIGATION_MODEL_UNSPECIFIED%22%2C%22likeButton%22%3A%7B%22likeButtonRenderer%22%3A%7B%22likesAllowed%22%3Atrue%2C%22likeStatus%22%3A%22INDIFFERENT%22%2C%22likeCountText%22%3A%7B%22simpleText%22%3A%22Like%22%7D%2C%22dislikeCountText%22%3A%7B%22simpleText%22%3A%22Dislike%22%7D%7D%7D%2C%22viewCommentsButton%22%3A%7B%22buttonRenderer%22%3A%7B%22icon%22%3A%7B%22iconType%22%3A%22SHORTS_COMMENT%22%7D%2C%22text%22%3A%7B%22simpleText%22%3A%22Comment%22%7D%7D%7D%2C%22shareButton%22%3A%7B%22buttonRenderer%22%3A%7B%22icon%22%3A%7B%22iconType%22%3A%22SHORTS_SHARE%22%7D%2C%22text%22%3A%7B%22simpleText%22%3A%22Share%22%7D%7D%7D%2C%22menu%22%3A%7B%22menuRenderer%22%3A%7B%22items%22%3A%5B%7B%22menuServiceItemRenderer%22%3A%7B%7D%7D%5D%7D%7D%2C%22pivotButton%22%3A%7B%22pivotButtonRenderer%22%3A%7B%22backgroundColor%22%3A%22THEME_ATTRIBUTE_OVERLAY_BACKGROUND_MEDIUM%22%2C%22icon%22%3A%7B%22iconType%22%3A%22WAVEFORM%22%7D%7D%7D%7D%7D%2C%22params%22%3A%22CAwaEwjQzYWM7-aHAxXiS_UFHWg5AgYqAA%253D%253D%22%2C%22onPlaybackCommand%22%3A%7B%22clickTrackingParams%22%3A%22CBwQ7fkGGAAiEwj3m4SM7-aHAxXQWA8CHVL0ADQ%3D%22%2C%22commandExecutorCommand%22%3A%7B%7D%7D%2C%22loggingContext%22%3A%7B%22vssLoggingContext%22%3A%7B%22serializedContextData%22%3A%22CgIIDA%253D%253D%22%7D%2C%22qoeLoggingContext%22%3A%7B%22serializedContextData%22%3A%22CgIIDA%253D%253D%22%7D%7D%2C%22ustreamerConfig%22%3A%22CAw%3D%22%7D%7D',
            'origin': 'https://www.youtube.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.youtube.com/shorts/BXeGvARVdYI',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"127.0.6533.99"',
            'sec-ch-ua-full-version-list': '"Not)A;Brand";v="99.0.0.0", "Google Chrome";v="127.0.6533.99", "Chromium";v="127.0.6533.99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            # 'x-client-data': 'CIm2yQEIorbJAQipncoBCKTuygEIlqHLAQiVossBCO+YzQEIhaDNAQiOqM4BCNWszgEI1q/OAQjlr84BCIuyzgEIpbLOAQjGts4BCNq3zgEYoJ3OARjJn84BGJyxzgE=',
            'x-goog-authuser': '0',
            # 'x-goog-visitor-id': 'CgswU3k0Wmw4N0RuQSiM_9W1BjIKCgJDThIEGgAgJg%3D%3D',
            'x-origin': 'https://www.youtube.com',
            'x-youtube-bootstrap-logged-in': 'true',
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20240808.00.00',
        }

        params = {
            'prettyPrint': 'false',
        }

        json_data = {
            'context': {
                'client': {
                    'hl': 'en',
                    'gl': 'HK',
                    'remoteHost': '101.44.81.255',
                    'deviceMake': '',
                    'deviceModel': '',
                    'visitorData': 'CgswU3k0Wmw4N0RuQSiXtMa1BjIKCgJDThIEGgAgJg%3D%3D',
                    'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36,gzip(gfe)',
                    'clientName': 'WEB',
                    'clientVersion': '2.20240805.01.00',
                    'osName': 'Windows',
                    'osVersion': '10.0',
                    'originalUrl': f'https://www.youtube.com/shorts/{video_id}',
                    'screenPixelDensity': 2,
                    'platform': 'DESKTOP',
                    'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                    'configInfo': {
                        'appInstallData': 'CJe0xrUGEI_EsAUQieiuBRDh7LAFENbdsAUQjcywBRC1sf8SEMzfrgUQppOxBRDqw68FEPyFsAUQqJKxBRCIh7AFEJSJsQUQppqwBRD2q7AFEO6irwUQt-r-EhC9tq4FEJbA_xIQ0-GvBRDJ5rAFEOuZsQUQiOOvBRDl9LAFEKXC_hIQmvCvBRCop7EFEOLUrgUQpaWxBRCPlLEFEJ3QsAUQkp2xBRC3768FEIvPsAUQ2cmvBRCigbAFENCNsAUQqJOxBRDQ-rAFEM3XsAUQnaawBRCU_rAFEMSSsQUQjZSxBRC9irAFENqgsQUQ65OuBRCQkrEFEPSrsAUQqLewBRDbr68FEKaSsQUQ_4ixBRC6-LAFEKiasAUQ1-mvBRDj0bAFEJaVsAUQyfevBRC9mbAFELDusAUQlqOxBRDK-bAFEKrYsAUQ8ZywBRDvzbAFEIO5_xIQ2aWxBRDHn7EFEOG8_xIQ3ej-EhCZmLEFELHcsAUQ3_WwBRDuiLEFEMnXsAUQ6-j-EhCvobEFEKKdsQUQ1KGvBRDViLAFEMmisQUQoImxBRDzwf8SKiBDQU1TRWhVSm9MMndETkhrQnZQdDhRdUI5d0VkQnc9PQ%3D%3D',
                    },
                    'screenDensityFloat': 1.5,
                    'userInterfaceTheme': 'USER_INTERFACE_THEME_LIGHT',
                    'timeZone': 'Asia/Shanghai',
                    'browserName': 'Chrome',
                    'browserVersion': '127.0.0.0',
                    'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'deviceExperimentId': 'ChxOek01T1RnMk5UQTROamM1TkRneE56RTNNdz09EJe0xrUGGJe0xrUG',
                    'screenWidthPoints': 1707,
                    'screenHeightPoints': 416,
                    'utcOffsetMinutes': 480,
                    'memoryTotalKbytes': '8000000',
                    'clientScreen': 'WATCH',
                    'mainAppWebInfo': {
                        'graftUrl': f'/shorts/{video_id}',
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
                    'isPrefetch': True,
                },
                'clickTracking': {
                    'clickTrackingParams': 'CBcQ7fkGGAAiEwist-_rt9-HAxX8YfUFHbBpK50=',
                },
                'adSignalsInfo': {
                    'params': [
                        {
                            'key': 'dt',
                            'value': '1722915350579',
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
                            'value': '1',
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
                            'value': '920',
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
                            'value': '416',
                        },
                        {
                            'key': 'biw',
                            'value': '1707',
                        },
                        {
                            'key': 'brdim',
                            'value': '0,0,0,0,1707,0,1707,920,1707,416',
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
                    'bid': 'ANyPxKrDhOYpqa6LoXus6Q4IDOZvY_AfMQpUDGEj3P8OUjdrIvLByGRisBiRAjqBVAdnjm_HztYqvzUVrRCHL9qebSeiUezsvg',
                },
            },
            'videoId': f'{video_id}',
            'params': 'AEByAMTwATygaHp1c3Rn5UBogYVAQEy3BI0n88V4LmNiizKWq7bQ3hXqgZDQU9BckJGdUJuR3FNblZVNkVsMzd1S28wRVBuOWRiajJNSE44cWpfa2JlVlBmRTZIQXNLVWdENllCekhBSXpYVHUxUQ',
            'playbackContext': {
                'contentPlaybackContext': {
                    'currentUrl': f'/shorts/{video_id}',
                    'vis': 0,
                    'splay': False,
                    'autoCaptionsDefaultOn': False,
                    'autonavState': 'STATE_ON',
                    'html5Preference': 'HTML5_PREF_WANTS',
                    'signatureTimestamp': 19936,
                    'referer': 'https://www.youtube.com/shorts/BXeGvARVdYI',
                    'lactMilliseconds': '-1',
                    'watchAmbientModeContext': {
                        'watchAmbientModeEnabled': True,
                    },
                },
                'prefetchPlaybackContext': {},
            },
            'racyCheckOk': False,
            'contentCheckOk': False,
        }

        response = requests_with_retry.post(
            'https://www.youtube.com/youtubei/v1/player',
            params=params,
            cookies=self.cookies,
            headers=headers,
            json=json_data,
            proxies=self.proxies,
        ).json()
        return response['videoDetails']

    def ytb_short_video(self, video_id):
        response = requests_with_retry.get(f'https://www.youtube.com/shorts/{video_id}', cookies=self.cookies,
                                           proxies=self.proxies, headers=self.headers).text
        item = YtbVideoItem()
        item.video_id = video_id
        avatar_list = re.findall('"channelThumbnail":\s*\{"thumbnails":\s*(\[[^]]*?\])', response)
        item.follower_count = None
        item.avatar = json.loads(avatar_list[0])[-1]['url']
        item.comment_count = int(
            re.findall('"viewCommentsButton":.*?"simpleText":\s*"([^"]*?)"', response)[0].replace(',', ''))
        item.content = None
        video_detail = self.get_short_video_duration(video_id)
        item.duration = int(video_detail['lengthSeconds'].replace('"', ''))
        item.title = video_detail['title']
        # item.title = re.findall('"accessibility":\{"accessibilityData":\{"label":"([^"]*?) @[^@]*?ago"}',response)[0]
        item.like_count = int(re.findall('"likeStatus":"INDIFFERENT","likeCount":(\d+),', response)[0])
        publish_time = re.findall('"publishDate":\{"simpleText":"([^"]*?)"}', response)[0]
        try:
            item.publish_time = int(datetime.datetime.strptime(publish_time, "%b %d, %Y").timestamp()) * 1000
        except:
            item.publish_time = int(datetime.datetime.strptime(publish_time, "%Y年%m月%d日").timestamp()) * 1000
        item.user_id = re.findall('"commandMetadata":\{"webCommandMetadata":\{"url":"/(@[^"]*?)"', response)[0]
        item.user_url = f"https://www.youtube.com/{item.user_id}"
        item.user_name = re.findall('"channel":\{"simpleText":"([^"]*?)"}', response)[0]
        item.video_cover_image = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        item.video_url = f'https://www.youtube.com/shorts/{video_id}'
        try:
            item.view_count = int(
                re.findall('\{"simpleText":"Views"},"accessibilityText":"([^ ]*?) views"}', response)[0].replace(',',
                                                                                                                 ''))
        except:
            item.view_count = int(
                re.findall('\{"simpleText":"观看次数"},"accessibilityText":"([^ ]*?)次观看"}', response)[0].replace(',',
                                                                                                                    ''))
        print(item.__dict__)
        return item.__dict__

    def get_authorization(self):
        ytb_short_js = """
        var TOKEN = "__fw"; // APISID / SAPISID token (base64)
var DOMAIN = "https://www.youtube.com"; // Domain name, including https://, without trailing slash

var $gb = function () {
  function a() {
    e[0] = 1732584193;
    e[1] = 4023233417;
    e[2] = 2562383102;
    e[3] = 271733878;
    e[4] = 3285377520;
    n = m = 0
  }
  function b(p) {
    for (var r = g, t = 0; 64 > t; t += 4) r[t / 4] = p[t] << 24 | p[t + 1] << 16 | p[t + 2] << 8 | p[t + 3];
    for (t = 16; 80 > t; t++) p = r[t - 3] ^ r[t - 8] ^ r[t - 14] ^ r[t - 16],
    r[t] = (p << 1 | p >>> 31) & 4294967295;
    p = e[0];
    var x = e[1],
    y = e[2],
    A = e[3],
    K = e[4];
    for (t = 0; 80 > t; t++) {
      if (40 > t) if (20 > t) {
        var L = A ^ x & (y ^ A);
        var U = 1518500249
      } else L = x ^ y ^ A,
      U = 1859775393;
       else 60 > t ? (L = x & y | A & (x | y), U = 2400959708) : (L = x ^ y ^ A, U = 3395469782);
      L = ((p << 5 | p >>> 27) & 4294967295) +
      L + K + U + r[t] & 4294967295;
      K = A;
      A = y;
      y = (x << 30 | x >>> 2) & 4294967295;
      x = p;
      p = L
    }
    e[0] = e[0] + p & 4294967295;
    e[1] = e[1] + x & 4294967295;
    e[2] = e[2] + y & 4294967295;
    e[3] = e[3] + A & 4294967295;
    e[4] = e[4] + K & 4294967295
  }
  function c(p, r) {
    if ('string' === typeof p) {
      p = unescape(encodeURIComponent(p));
      for (var t = [
      ], x = 0, y = p.length; x < y; ++x) t.push(p.charCodeAt(x));
      p = t
    }
    r || (r = p.length);
    t = 0;
    if (0 == m) for (; t + 64 < r; ) b(p.slice(t, t + 64)),
    t += 64,
    n += 64;
    for (; t < r; ) if (f[m++] = p[t++], n++, 64 == m) for (m = 0, b(f); t + 64 < r; ) b(p.slice(t, t + 64)),
    t += 64,
    n += 64
  }
  function d() {
    var p = [
    ],
    r = 8 * n;
    56 > m ? c(h, 56 - m) : c(h, 64 - (m - 56));
    for (var t = 63; 56 <= t; t--) f[t] = r & 255,
    r >>>= 8;
    b(f);
    for (t = r = 0; 5 > t; t++) for (var x = 24; 0 <= x; x -= 8) p[r++] = e[t] >> x & 255;
    return p
  }
  for (var e = [
  ], f = [
  ], g = [
  ], h = [
    128
  ], k = 1; 64 > k; ++k) h[k] = 0;
  var m,
  n;
  a();
  return {
    reset: a,
    update: c,
    digest: d,
    digestString: function () {
      for (var p = d(), r = '', t = 0; t < p.length; t++) r += '0123456789ABCDEF'.charAt(Math.floor(p[t] / 16)) + '0123456789ABCDEF'.charAt(p[t] % 16);
      return r
    }
  }
}

var hash = $gb();
var date = Math.floor(new Date() / 1000);
hash.update(date + " " + TOKEN + " " + DOMAIN);
var result = date + "_" + hash.digestString().toLowerCase();
process.stdout.write(result);
        """
        SAPISID = self.cookies.get('SAPISID')
        current_dir_path = os.path.abspath(os.path.dirname(__file__))
        # print('current_dir_path:', current_dir_path)
        # with open(current_dir_path + '\ytb_short_video.js', 'r', encoding='utf-8') as f:
        #     js_code = f.read()

        js_code = ytb_short_js.replace('__fw', SAPISID)
        # execjs执行
        authorization_js_path = current_dir_path + f'/{int(time.time() * 1000)}.js'
        with open(authorization_js_path, 'w', encoding='utf-8') as f:
            f.write(js_code)
        result = subprocess.check_output(['node', authorization_js_path], text=True).strip()
        print(result)
        os.remove(authorization_js_path)
        return result

