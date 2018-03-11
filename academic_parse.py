from bs4 import BeautifulSoup
import urllib.parse as urlencode

LAST_HTML = ''

def load_word_html_data(word, session):
    word = urlencode.quote_plus(str(word))
    url = 'https://dic.academic.ru/searchall.php?SWord={}&from=xx&to=ru&did=&stype='.format(word)
    request = session.get(url)
    return request.text


def get_article_text(article):
    paragraph = article.find('p')
    UNDESIRED_PREFIX = ' — '
    t = paragraph.contents[3]
    if t.startswith(UNDESIRED_PREFIX):
        t = t[len(UNDESIRED_PREFIX):]
    t = t.strip()
    return t


def get_article_href(article):
    paragraph = article.find('p')
    article_href = paragraph.find('strong').find('a', href=True)['href']
    return article_href


def get_article_dic(article):
    dic = article.find('p', {'class': 'src'}).find('a', href=True)

    return {
        "name": dic.text,
        "href": dic['href']
    }


def get_word_definition(article):
    return {
        'text': get_article_text(article),
        'href': get_article_href(article),
        'dic': get_article_dic(article)
    }


def get_word_definitions(html_text):
    soup = BeautifulSoup(html_text, "lxml")

    found_articles = soup.find('ul', {
        'id': 'found_articles'
    }).find_all('li')

    definitions = []
    for article in found_articles:
        try:
            definition = get_word_definition(article)
            definitions.append(definition)
        except:
            print("Academic parse error!")

    return definitions


def download_word_definition(word, session):
    html_text = load_word_html_data(word, session)
    LAST_HTML = html_text
    defs = get_word_definitions(html_text)
    return defs