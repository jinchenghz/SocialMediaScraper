from SocialMediaScraper.twitter.tw_comment import TwComment
from SocialMediaScraper.twitter.tw_post import TwPost
from SocialMediaScraper.twitter.tw_post_list import TwPostList
from SocialMediaScraper.twitter.tw_search import TwSearch
from SocialMediaScraper.twitter.tw_user import twitter_user_info


def user_info(screen_name, cookies, proxies=None):
    """
    获取用户信息
    :param screen_name:
    :param cookies:
    :param proxies:
    :return:
    """
    return twitter_user_info(screen_name, cookies, proxies)


def post_list(user_id, cookies, post_num, proxies=None):
    """
    获取用户帖子列表
    :param user_id:
    :param cookies:
    :param post_num:
    :param proxies:
    :return:
    """
    return TwPostList(cookies,post_num=post_num, proxies=proxies).tw_post_list(user_id)


def post_detail(post_url, cookies, proxies=None):
    """
    获取帖子详情
    :param post_url:
    :param cookies:
    :param proxies:
    :return:
    """
    return TwPost(cookies, proxies=proxies).tw_post_detail(post_url)


def post_comments(post_id, cookies, comment_count, proxies=None):
    """
    获取帖子评论
    :param post_id:
    :param cookies:
    :param comment_count:
    :param proxies:
    :return:
    """
    return TwComment(cookies,comment_num=comment_count, proxies=proxies).get_comment_list(post_id)


def post_search(keyword, cookies, post_num, proxies=None):
    """
    关键词搜索帖子信息
    :param keyword:
    :param cookies:
    :param post_num:
    :param proxies:
    :return:
    """
    return TwSearch(cookies, proxies=proxies).twitter_post_search(keyword, post_num)
