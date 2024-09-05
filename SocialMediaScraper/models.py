class BaseItem:
    pass


class YtbUserItem:
    user_name = None
    user_id = None
    user_url = None
    description = None
    avatar = None
    video_count = None
    view_count = None
    follower_count = None


class YtbPostListItem(BaseItem):
    post_id = None
    post_url = None
    title = None
    publish_time = None


class YtbVideoItem:
    avatar = None
    follower_count = None
    title = None
    content = None
    publish_time = None
    duration = None
    view_count = None
    video_cover_image = None
    user_name = None
    user_url = None
    user_id = None
    video_id = None
    video_url = None
    like_count = None
    comment_count = None


class YtbCommentItem(BaseItem):
    comment_id = None
    comment_content = None
    comment_time = None
    comment_like_count = None
    comment_replay_count = None
    comment_user_name = None
    comment_user_id = None
    comment_user_url = None
    comment_user_avatar = None


class YtbPostSearchItem(BaseItem):
    content = None
    create_time = None
    duration = None
    followers = None
    image_list = None
    post_id = None
    post_url = None
    title = None
    user_avatar = None
    user_id = None
    user_name = None
    user_url = None
    video_cover_image = None
    view_count = None
