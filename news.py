from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from dateutil import parser as ps

from const import NEWS_URL_BM, NEWS_URL_ML
from telegram import publish_article
from utils import fix_last_dharko, merge_sources, replace_this


# scrape section: a function that starts the scraping engine

def scrape_articles(url: str) -> BeautifulSoup:
    parser = 'lxml'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36\
            (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        content = response.text.encode('utf-8')
        soup = BeautifulSoup(content, parser)
        return soup
    except requests.exceptions.ConnectionError as e:
        return print("Looks like the news API did an oopsie:\n", e)


# sources section: the article sources will be in this section organized by function names

def bizmandu() -> List[Dict[str, Optional[Union[datetime, str]]]]:
    source = 'bizmandu'
    first_word = "^काठमाडौं['\s']?[।]?"
    soup = scrape_articles(NEWS_URL_BM)
    container = soup.select_one("ul.uk-list").select('li')
    articles = []

    for article in container:
        # dont touch! just witness the magic
        url = article.find('a')['href']
        title = article.find('h3').text.strip()
        lines = article.find_all('p', {'class': False, 'id': False})
        excerpt = ' '.join([line.text.strip() for line in lines]).strip()
        description = replace_this(first_word, excerpt)
        raw_date = article.select_one('p.uk-article-meta').text.strip()
        date = ps.parse(raw_date.split('बिजमाण्डू')[1].strip())

        the_article = {
            "date_published": date,
            "description": fix_last_dharko(description),
            "image_url": None,
            "lang": "nepali",
            "source": source,
            "title": title,
            "url": url,
        }

        articles.append(the_article)

    return articles


def merolagani() -> List[Dict[str, Optional[Union[datetime, str]]]]:
    source = 'merolagani'
    soup = scrape_articles(NEWS_URL_ML)
    container = soup.select('div.media-news')
    articles = []

    for article in container:
        # dont touch! just witness the magic
        raw_url = article.find('a')['href']
        url = f'https://{source}.com{raw_url}'
        title = article.select('h4.media-title > a')[0].text.strip()
        image_url = article.find('img')['src']
        raw_date = article.select('span.media-label')[0].text.strip()
        date = ps.parse(raw_date)

        the_article = {
            "date_published": date,
            "description": None,
            "image_url": image_url,
            "lang": "nepali",
            "source": source,
            "title": title,
            "url": url,
        }

        articles.append(the_article)

    return articles


# main section: combines all required functions and executes them

def latest_articles() -> List[Dict]:
    return merge_sources(bizmandu())


def main():
    from insert import add_article, unsent_articles

    # fetch and store new articles before publishing to the channel
    add_article()

    unpublished_articles = list(unsent_articles())
    if unpublished_articles:
        from models import session

        # articles that are older has to be published first
        # making the latest ones to be after the older ones
        the_list = unpublished_articles[::-1]
        for the_article in the_list:
            publish_article(the_article)
        session.commit()
        return print(f"published {len(unpublished_articles)} articles")


if __name__ == '__main__':
    main()
