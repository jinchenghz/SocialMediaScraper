from SocialMediaScraper.facebook.fb_post import FbPost
from SocialMediaScraper.facebook.fb_post_list import FbPostList
from SocialMediaScraper.facebook.fb_search import FBSearch
from SocialMediaScraper.facebook.fb_user import FBUser


def user_info(user_id, cookies, proxies=None):
    """
    获取用户信息
    :param proxies:
    :param user_id:用户id
    :param cookies:浏览器cookies
    :return:
    """
    return FBUser(cookies, proxies=proxies).fb_user(user_id)


def post_list(user_id, cookies, post_num, proxies=None):
    """
    获取用户发帖列表
    :param user_id: 用户id
    :param cookies: 浏览器cookies
    :param post_num: 需要爬取的帖子数
    :param proxies: 代理信息
    :return:
    """
    return FbPostList(cookies, proxies=proxies).get_post_list(user_id, post_num)


def post_detail(post_url, cookies, proxies=None):
    """
    获取帖子详情
    :param post_url: 帖子链接
    :param cookies: 浏览器cookies
    :param proxies: 代理信息

    :return:
    """
    return FbPost(cookies, proxies=proxies).get_post_detail(post_url)


def post_comments(post_url, cookies, comment_count, proxies=None):
    """
    获取帖子评论信息
    :param post_url: 帖子链接
    :param cookies: 浏览器cookies
    :param comment_count: 需要抓取的评论数
    :param proxies: 代理信息
    :return:
    """
    return FbPost(cookies, proxies=proxies).fb_comment(post_url, comment_count)


def search_post(keyword, cookies, post_num, proxies=None):
    """
    搜索帖子
    :param proxies:
    :param keyword: 关键词
    :param cookies: 浏览器cookies
    :param post_num: 需要爬取的帖子数
    :return:
    """
    return FBSearch(cookies, proxies=proxies).fb_search_post(keyword, post_num)
