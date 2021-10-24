import requests
from bs4 import BeautifulSoup as bs
from requests_cache import install_cache
from urllib.parse import urlparse, urljoin


cache_time = 60 * 60 * 24
install_cache("rss_cache", backend="sqlite", expire_after=cache_time)
# install_cache("html_cache", backend="sqlite", expire_after=cache_time)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
}
url = "https://architectureau.com/rss"
url_parts = urlparse(url)
if not url_parts.netloc:
    exit(f"{url} is not a url")
else:
    base_url = f"{url_parts.scheme}://{url_parts.netloc}"


S = requests.get(url, headers=headers)
# print("location", S.headers['location'])

soup = bs(S.text, "lxml")
# print(soup)


def full_url(a):
    url_parts = urlparse(a)
    if url_parts.netloc:
        return a
    else:
        response = urljoin(base_url, a)
        return response


feed_urls = []
for res in soup.find_all("a"):
    if 'href' in res.attrs:
        if 'rss' in res['href'].lower():
            feed_urls.append(full_url(res['href']))


print(feed_urls)
