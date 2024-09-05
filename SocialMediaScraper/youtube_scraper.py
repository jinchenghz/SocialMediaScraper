import re

from SocialMediaScraper.facebook.fb_post import FbPost
from SocialMediaScraper.facebook.fb_search import FBSearch
from SocialMediaScraper.youtube.ytb_comment import YtbComment
from SocialMediaScraper.youtube.ytb_post import YtbPost
from SocialMediaScraper.youtube.ytb_post_list import YtbPostList
from SocialMediaScraper.youtube.ytb_search import YTBSearch
from SocialMediaScraper.youtube.ytb_user import YtbUser


def user_info(user_id, cookies, proxies=None,user_agent=None):
    """
    获取用户信息
    :param user_agent:
    :param proxies:
    :param user_id:用户id
    :param cookies:浏览器cookies
    :return:
    """
    return YtbUser(cookies, proxies=proxies, user_agent=user_agent).ytb_user(user_id)


def post_list(user_id, cookies, post_num, proxies=None):
    """
    获取用户发帖列表
    :param user_id: 用户id
    :param cookies: 浏览器cookies
    :param post_num: 需要爬取的帖子数
    :param proxies: 代理信息
    :return:
    """
    return YtbPostList(cookies, proxies=proxies,post_num=post_num).post_list(user_id)


def post_detail(post_url, cookies, proxies=None):
    """
    获取帖子详情
    :param post_url: 帖子链接
    :param cookies: 浏览器cookies
    :param proxies: 代理信息

    :return:
    """
    pattern = re.search(r'https://www\.youtube\.com/watch\?v=([^? ]*)', post_url)
    if pattern:
        response = YtbPost(cookies=cookies, proxies=proxies).ytb_post_detail(pattern.group(1))
    else:
        pattern = re.search(r'https://www\.youtube\.com/shorts/([^? ]*)', post_url)
        if not pattern:
            raise Exception("视频链接错误")
        response = YtbPost(cookies=cookies, proxies=proxies).ytb_short_video(pattern.group(1))

    return response


def post_comments(post_url, cookies, comment_num, proxies=None):
    """
    获取帖子评论信息
    :param comment_num: 需要抓取的评论数
    :param post_url: 帖子链接
    :param cookies: 浏览器cookies
    :param proxies: 代理信息
    :return:
    """
    return YtbComment(cookies,comment_num=comment_num, proxies=proxies).get_comments_data(post_url)


def search_post(keyword, cookies, post_num, proxies=None):
    """
    搜索帖子
    :param proxies:
    :param keyword: 关键词
    :param cookies: 浏览器cookies
    :param post_num: 需要爬取的帖子数
    :return:
    """
    return YTBSearch(cookies,post_num=post_num, proxies=proxies).youtube_post_search(keyword, post_num)

