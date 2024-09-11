import json
import re
from pprint import pprint

import requests
from jsonpath_ng import parse

from SocialMediaScraper.models import FbPostItem


params = {
    'story_fbid': 'pfbid02ahr6PAyU8fzQqnNj9w4U4nhDt3uYnQ7KnstMhn3k5jiPGhp39oDQ26QGRaWBW7kzl',
    'id': '61553498740610',
}

response = requests.get('https://www.facebook.com/permalink.php', params=params, cookies=cookies, headers=headers).text

ret = re.findall('<script[^>]*?>(.*?)</script>', response)
for r in ret:
    if "comet_sections" in r:
        json_data = json.loads(r)
        edge = parse("$..result").find(json_data)[0].value['data']
        item = FbPostItem()
        item.post_id = edge['node']['post_id']
        item.action_id = edge['node']['feedback']['id']
        comet_sections = edge['node']['comet_sections']
        try:
            item.content = comet_sections['content']['story']['comet_sections']['message']['story']['message']['text']
        except:
            item.content = None
        item.publish_time = parse("$..creation_time").find(comet_sections)[0].value*1000
        item.reaction_count = [_data.value["count"] for _data in parse("$..reaction_count").find(comet_sections) if
                               isinstance(_data.value, dict) and 'count' in _data.value][0]
        item.comments_count = parse("$..comments").find(comet_sections)[0].value["total_count"]
        item.share_count = [_data.value["count"] for _data in parse("$..share_count").find(comet_sections) if
                            isinstance(_data.value, dict) and 'count' in _data.value][0]
        story_list = parse("$..story").find(comet_sections)
        for story in story_list:
            story_data = story.value
            if story_data.get("creation_time"):
                item.post_url = story_data.get("url")
        if not item.post_url:
            print('post_url获取失败')
            raise Exception('post_url获取失败')
            # return

            # 获取媒体信息
        attachments = parse("$..all_subattachments").find(comet_sections)
        item.image_list = []
        for attachment in attachments:
            if not attachment.value.get("count"):
                continue
            item.image_list = [i.value["uri"] for i in parse("$..viewer_image").find(attachment.value)]

        item.video_url = None
        item.duration = None
        item.video_cover_image = None
        _attachments = parse("$..attachments").find(comet_sections)
        for attachment in _attachments:
            attachment = attachment.value
            if not attachment:
                continue
            if attachment[0].get("deduplication_key"):
                # 短视频
                short_form_video_context = parse("$..short_form_video_context").find(attachment[0])
                if short_form_video_context:
                    short_video = short_form_video_context[0].value["playback_video"]
                    item.video_url = short_video.get("browser_native_hd_url") if short_video.get(
                        "browser_native_hd_url") else short_video.get("browser_native_sd_url")
                    item.duration = int(short_video['length_in_second'])
                    item.video_cover_image = short_video['preferred_thumbnail']['image']['uri']
                    continue
                # 长视频
                long_video = parse("$..media").find(attachment[0])
                if long_video:
                    long_video = long_video[0].value
                    if long_video.get("__typename") == "Video":
                        item.video_url = long_video.get("browser_native_hd_url") if long_video.get(
                            "browser_native_hd_url") else long_video.get("browser_native_sd_url")
                        item.video_cover_image = long_video["thumbnailImage"]["uri"]
                        item.duration = int(long_video["playable_duration_in_ms"] / 1000)
        # 获取用户信息
        item.user_id = None
        item.user_url = None
        item.user_name = None
        item.avatar = None
        actors = parse("$..actors").find(comet_sections)
        owning_profile_id = parse("$..owning_profile").find(comet_sections)[0].value["id"]
        for actor in actors:
            for user in actor.value:
                if 'profile_picture' in user and user['id'] == owning_profile_id:
                    item.user_id = user['id']
                    item.user_url = user['profile_url']
                    item.user_name = user['name']
                    item.avatar = user['profile_picture']['uri']

        pprint(item.__dict__)
