## Main functions of the project:
This project mainly crawls data from foreign social networks such as Facebook, Instagram, and Twitter, You only need to provide cookies to get the data you want:
### facebook_scraper module
1. Get Facebook user information
2. Get Facebook user post list
3. Get Facebook post details
4. Get Facebook post comment information
5. Facebook post search function

### instagram_scraper module
1. Get Instagram user information
2. Get Instagram user post list
3. Get Instagram post details
4. Get Instagram post comment information
5. Instagram post search function

### twitter_scraper module
1. Get Twitter (renamed X, the same below) user information
2. Get Twitter user post list
3. Get Twitter post details
4. Get Twitter post comment information
5. Twitter post search function


## Usage examples
1.facebook_scraper
```python

from SocialMediaScraper import facebook_scraper

fb_cookies = {"cookie sample": 'cookie sample'}


facebook_scraper.search_post('US President Elect', cookies=fb_cookies, post_num=10)

facebook_scraper.post_comments('https://www.facebook.com/joebiden/videos/813793037198888', cookies=fb_cookies,
                               comment_count=10)

facebook_scraper.post_detail('https://www.facebook.com/joebiden/videos/813793037198888', cookies=fb_cookies)

facebook_scraper.post_list('joebiden', cookies=fb_cookies, post_num=20)

facebook_scraper.user_info('joebiden', cookies=fb_cookies)

```
2. instagram_scraper
```python
from SocialMediaScraper import instagram_scraper

ins_cookies = {"cookie sample": 'cookie sample'}
instagram_scraper.search_post('hangzhou', post_num=10, cookies=ins_cookies)

instagram_scraper.post_comments('https://www.instagram.com/p/C-FU96JyZy1/', post_num=10, cookies=ins_cookies)

instagram_scraper.post_detail('https://www.instagram.com/p/C-FU96JyZy1/', cookies=ins_cookies)

instagram_scraper.post_list('hheejinkimm', cookies=ins_cookies, post_num=10)

instagram_scraper.user_info('hheejinkimm', cookies=ins_cookies)
```

3.twitter_scraper
```python

from SocialMediaScraper import twitter_scraper

twitter_cookies =  {"cookie sample": 'cookie sample'}
twitter_scraper.post_search('US President Elect', post_num=20, cookies=twitter_cookies)


twitter_scraper.post_comments('https://x.com/Pismo_B/status/1794195521755885996', cookies=twitter_cookies,
                              comment_count=10)

twitter_scraper.post_detail('https://x.com/Pismo_B/status/1794195521755885996', cookies=twitter_cookies)

twitter_scraper.post_list('22wiggins', cookies=twitter_cookies, post_num=20)

twitter_scraper.user_info('22wiggins', cookies=twitter_cookies)
```