from urllib import request
from bs4 import BeautifulSoup
import itertools
from urllib.parse import urlparse
import os


def get_bs4(url):
    with request.urlopen(url) as response:
        soup = BeautifulSoup(response, "html.parser")
    return soup


## 記事のURL一覧を取得する
def get_article_urls():
    titles_css_selector = "#main > div.skin-blogArchive > div.skin-blogArchiveBody.skin-bgMain > ul > li > div > div:nth-child(2) > h2 > a"
    max_url = ""
    articles = []
    for i in itertools.count(1):
        print(i)
        url = f"https://ameblo.jp/angerme-new/entrylist-{i}.html"
        partial_url = f"/angerme-new/entrylist-{i}.html"
        if partial_url == max_url:
            break
        soup = get_bs4(url)
        if i == 1:
            max_url = soup.select("#indexPagination > ul.skin-paginationNexts > li:nth-child(2) > a")[0].get("href")
        for j in soup.select(titles_css_selector):
            blog_url = j.get("href")
            yield blog_url
            print(blog_url)


## 記事から画像のリンクを取得する
def get_picture_links(article_url):
    soup = get_bs4(article_url)
    links = set()
    for i in soup.select("img"):
        link = i.get("src")
        if "user_images" not in link:
            continue
        links.add(link.replace("?caw=800", ""))
    return links


if __name__ == "__main__":
    base_url = "https://ameblo.jp"
    for url in get_article_urls():
        article_url = base_url + url
        for link in get_picture_links(article_url):
            print(link)
            output_filename = os.path.basename(urlparse(link).path)
            request.urlretrieve(link, output_filename)