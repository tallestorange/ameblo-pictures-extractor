from urllib import request
from bs4 import BeautifulSoup
import itertools
from urllib.parse import urlparse
import os
import datetime


def get_bs4(url):
    with request.urlopen(url) as response:
        soup = BeautifulSoup(response, "html.parser")
    return soup


## 記事のURL一覧を取得する
def get_article_urls(blog_id):
    titles_css_selector = "#main > div.skin-blogArchive > div.skin-blogArchiveBody.skin-bgMain > ul > li > div > div:nth-child(2) > h2 > a"
    max_url = ""
    articles = []
    for i in itertools.count(1):
        print(i)
        url = f"https://ameblo.jp/{blog_id}/entrylist-{i}.html"
        partial_url = f"/angerme-new/entrylist-{i}.html"
        soup = get_bs4(url)
        if i == 1:
            max_url = soup.select("#indexPagination > ul.skin-paginationNexts > li:nth-child(2) > a")[0].get("href")
        for j in soup.select(titles_css_selector):
            blog_url = j.get("href")
            yield blog_url
        print()
        if partial_url == max_url:
            break


## 記事から画像のリンクを取得する
def get_picture_links(article_url):
    soup = get_bs4(article_url)

    raw_html = str(soup)

    # 記事を書いた日を求める
    date_published = raw_html.find("datePublished")
    if date_published == -1:
        dt = None
    else:
        iso_datetime_string = raw_html[date_published+16:date_published+45]
        dt = datetime.datetime.fromisoformat(iso_datetime_string)

    # だれにタグ付けされているかを求める
    theme_name = ""
    for s in raw_html[raw_html.find("theme_name")+13:]:
        if s == '"':
            break
        theme_name += s

    links = set()
    for i in soup.select("img"):
        link = i.get("src").replace("?caw=800", "")
        if "user_images" not in link:
            continue
        links.add((link, dt, theme_name))
    return links


if __name__ == "__main__":
    base_url = "https://ameblo.jp"
    blogs = [
        "angerme-new",
        "angerme-ss-shin",
        "angerme-amerika"
    ]
    for blog in blogs:
        for url in get_article_urls(blog):
            article_url = base_url + url
            for link, dt, theme_name in get_picture_links(article_url):
                if dt is None:
                    dt_str = "YYYYmmddHHMMSS"
                else:
                    dt_str = dt.strftime("%Y%m%d%H%M%S")
                filename = os.path.basename(urlparse(link).path)
                print(dt_str, theme_name, link)
                output_filename = f"{theme_name}_{dt_str}_{filename}"
                request.urlretrieve(link, output_filename)