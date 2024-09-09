class InsUserItem:
    user_name = None
    user_id = None
    user_url = None
    avatar = None
    followers_count = None
    screen_name = None
    post_count = None


class InsPostListItem:
    post_id = None
    post_url = None
    content = None
    publish_time = None


class InsPostItem:
    media_id = None
    text = None
    publish_time = None
    like_count = None
    comment_count = None
    post_url = None
    coauthor_producers = None
    user_id = None
    user_name = None
    screen_name = None
    avatar = None
    image_list = None
    video_url = None
    video_cover_image = None
    video_duration = None


class InsCommentItem:
    comment_id = None
    user_id = None
    user_name = None
    screen_name = None
    avatar = None
    comment_content = None
    create_time = None
    like_num = None


class InsSearchItem:
    post_id = None
    post_url = None
    content = None
    publish_time = None
    user_id = None
    user_full_name = None
    user_name = None
    user_url = None
    avatar = None
    image_list = None
    like_count = None
    comment_count = None
    play_count = None
    video_url = None
    video_cover_image = None
    duration = None


class FbUserItem:
    user_name = None
    user_id = None
    user_url = None
    avatar = None
    followers_count = None
    friends_count = None
    likes_count = None
    following_count = None
    location = None
    gender = None
    birthday = None


class FbPostListItem:
    post_id = None
    action_id = None
    content = None
    publish_time = None
    post_url = None
    reaction_count = None
    comments_count = None
    share_count = None
    imageList = None
    video = None
    videoCoverImage = None
    duration = None


class FbPostItem:
    user_id = None
    user_url = None
    user_name = None
    avatar = None
    post_url = None
    action_id = None
    view_count = None
    react_count = None
    comment_count = None
    share_count = None
    content = None
    create_time = None
    post_id = None
    image_list = None
    video_url = None
    video_cover_image = None
    video_duration = None


class FbCommentItem:
    comment_id = None
    gender = None
    user_id = None
    user_name = None
    user_url = None
    avatar = None
    content = None
    likes_count = None
    create_time = None


class FbSearchItem:
    post_id = None
    action_id = None
    user_name = None
    user_id = None
    user_url = None
    avatar = None
    create_time = None
    post_url = None
    like_count = None
    share_count = None
    comment_count = None
    image_list = None
    video_list = None
    video_cover_image = None
    duration = None


class TwUserItem:
    avatar = None
    user_full_name = None
    favourites_count = None
    followers_count = None
    join_time = None
    friends_count = None
    location = None
    user_id = None
    user_name = None
    listed_count = None
    media_count = None
    statuses_count = None
    birthdate = None
    subscriptions_count = None


class TwPostListItem:
    user_id = None
    user_name = None
    views_count = None
    content = None
    bookmark_count = None
    favorite_count = None
    reply_count = None
    retweet_count = None
    post_id = None
    post_url = None
    publish_time = None


class TwPostItem:
    content = None
    publish_time = None
    favorite_count = None
    reply_count = None
    retweet_count = None
    bookmark_count = None
    views_count = None
    type = None
    post_id = None
    post_url = None
    image_list = None
    video_url = None
    video_cover_image = None
    video_duration = None


class TwCommentItem:
    comment_id = None
    user_name = None
    user_full_name = None
    user_url = None
    avatar = None
    user_id = None
    publish_time = None
    content = None
    favorite_count = None
    comment_url = None


class TwPostSearchItem:
    avatar = None
    user_id = None
    user_name = None
    user_full_name = None
    followers_count = None
    friends_count = None
    statuses_count = None
    post_id = None
    content = None
    publish_time = None
    favorite_count = None
    reply_count = None
    retweet_count = None
    bookmark_count = None
    views_count = None
    type = None
    post_url = None
    url = None
    image_list = None
    video_url = None
    video_cover_image = None
    duration = None


class YtbUserItem:
    user_name = None
    user_id = None
    user_url = None
    avatar = None
    followers_count = None
    description = None
    video_count = None
    view_count = None


class YtbPostListItem:
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


class YtbCommentItem:
    comment_id = None
    comment_content = None
    comment_time = None
    comment_like_count = None
    comment_replay_count = None
    comment_user_name = None
    comment_user_id = None
    comment_user_url = None
    comment_user_avatar = None


class YtbPostSearchItem:
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
