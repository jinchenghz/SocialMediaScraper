from SocialMediaScraper.instagram.ins_post import InsPost
from SocialMediaScraper.instagram.ins_post_list import InsPostList
from SocialMediaScraper.instagram.ins_search import InsSearch
from SocialMediaScraper.instagram.ins_user import get_user_data


def user_info(user_name, cookies, proxies=None):
    """
    获取ins用户信息
    :param user_name:
    :param cookies:
    :param proxies:
    :return:
    """
    return get_user_data(user_name, cookies, proxies=proxies)


def post_list(user_name, cookies, post_num, proxies=None):
    """
    获取ins用户帖子列表
    :param post_num:
    :param user_name:
    :param cookies:
    :param proxies:
    :return:
    """
    return InsPostList(cookies, proxies=proxies).get_post_list(user_name, post_num)


def post_detail(post_url, cookies, proxies=None):
    """
    获取ins帖子详情
    :param post_url:
    :param cookies:
    :param proxies:
    :return:
    """
    return InsPost(cookies, proxies=proxies).ins_post_detail(post_url)


def post_comments(post_url, cookies, post_num, proxies=None):
    """
    获取ins帖子评论
    :param post_url:
    :param post_num:
    :param cookies:
    :param proxies:
    :return:
    """
    return InsPost(cookies, proxies=proxies).get_comments(post_url,post_num)


def search_post(keyword, cookies, post_num, proxies=None):
    """
    搜索ins帖子
    :param keyword:
    :param cookies:
    :param post_num:
    :param proxies:
    :return:
    """
    return InsSearch(cookies, proxies=proxies).hashtag_post(keyword, post_num)
