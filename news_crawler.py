import re

import validators
from newspaper import Article

import requests
from bs4 import BeautifulSoup

import mysql.connector

from datetime import datetime

from rake_nltk import Rake
import yake

from summa import keywords

from google_trends import getRealtimeTrends
# import nltk
# nltk.download('punkt')


def process_keyword_text_rank(text):
    TR_keywords = keywords.keywords(text, scores=True)
    print(TR_keywords[0:10])


def process_key_word_yake(text):
    # punctuations = ".,;:?!()'\""
    text_tokenized = ViTokenizer.tokenize(text)
    # print(text_tokenized)
    stopwords = open('D:\\vietnamese-stopwords.txt', encoding="utf8").read().splitlines()
    # stopwords = open('D:\stopwords.txt', encoding="utf8").read().splitlines()

    kw_extractor = yake.KeywordExtractor(lan='vi', n=3, stopwords=stopwords)

    keywords = kw_extractor.extract_keywords(text)
    # keywords = kw_extractor.extract_keywords(text_tokenized)
    keywords_to_save = []
    for kw in keywords[0:3]:
        # print(kw[0])
        keywords_to_save.append(kw[0])
    # for kw in keywords:
    #     print(kw)
    # print(','.join(keywords_to_save))
    return ','.join(keywords_to_save)

def process_keyword_rake(text):
    punctuations = ".,;:?!()'\""
    # stopwords = open('D:\\vietnamese-stopwords.txt', encoding="utf8").read().splitlines()
    stopwords = open('D:\stopwords.txt', encoding="utf8").read().splitlines()
    text_tokenized = ViTokenizer.tokenize(text)

    r = Rake(stopwords, punctuations)

    # r.extract_keywords_from_text(text)
    r.extract_keywords_from_text(text_tokenized)
    # print(r.get_ranked_phrases_with_scores())
    return r.get_ranked_phrases_with_scores()[:3]


def is_url(url):
    return validators.url(url)


def get_article_text(url):
    if not is_url(url):
        result = {
            'url': url,
            'error': 'Url không hợp lệ!',
            'success': False
        }

        return result
    article = Article(url, language='vi')
    article.download()
    article.parse()
    article.nlp()

    return article.text


def crawl(url):
    if not is_url(url):
        result = {
            'url': url,
            'error': 'Url không hợp lệ!',
            'success': False
        }

        return result
    # article = Article(url, language='vi')
    article = Article(url, language='vi')
    article.download()
    article.parse()
    article.nlp()
    result = {'url': url, 'error': '', 'success': True, 'title': article.title,
              'keywords': ', '.join(article.keywords if article.keywords else (
                  article.meta_keywords if article.meta_keywords else article.meta_data.get('keywords', []))),
              # 'keywords': process_key_word_yake(article.text),
              'published_date': article.publish_date if article.publish_date
              else article.meta_data.get('pubdate', ''), 'top_img': article.top_image,
              'content': re.sub('\\n+', '</p><p>', '<p>' + article.text + '</p>'),
              'summary': article.summary, 'image': article.images, 'authors': article.authors}

    rs = (article.title, re.sub('\\n+', '</p><p>', '<p>' + article.text + '</p>')
          , article.top_image, article.summary
          , article.publish_date if article.publish_date else
          (article.meta_data.get('pubdate', '') if article.meta_data.get('pubdate', '') else datetime.now())
          # , ','.join(article.keywords if article.keywords else
          #            (article.meta_keywords if article.meta_keywords else article.meta_data.get('keywords', [])))
          , process_key_word_yake(article.text)
          # , process_keyword_rake(article.text)
          , url
          # , article.text
          )

    return rs


def crawl_article(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    menu_name = ''
    # get category info
    for menu_list in soup.find_all('ul', {"class": "breadcrumb"}):
        # print(menu_list)
        level = 0
        separator = ''
        for menu in menu_list.find_all('li'):
            menu_name = menu_name + separator + menu.find('a').get('title')
            separator = '/'
    # get title
    title = soup.find('h1', {'class': 'title-detail'}).text
    return title


def crawl_list_url():
    main_url = 'https://vnexpress.net/'
    html_text = requests.get(main_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    cnt = 0
    for article in soup.find_all('article'):
        link = article.find('a')
        if is_url(link.get('href')):
            cnt = cnt + 1
            print(link.get('href'))
            # print('-----------------------')
            # print(crawl(link.get('href')))
            # print(crawl_article(link.get('href')))
            # print('-----------------------')
    print(cnt)


def saveNewsToDb():
    try:
        connection = mysql.connector.connect(host='localhost', database='news', user='root', password='Trongduc2206')
        # print(connection)
        cursor = connection.cursor();

        sql = 'insert into news (title, topic_id, content, image_url, abstract, pub_date, keyword, news_key, status, create_time, update_time) values (%s, %d, %s, %s, %s, %s, %s, 1, now(), now() )'
        # val =
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))
    # finally:
    #     if connection.is_connected():
    #         print("MySQL is connected");
    #         cursor.close()
    #         connection.close()
    #         print("MySQL connection is closed")


def crawl_list_by_topic(topic):
    main_url = 'https://vnexpress.net/'
    url_topic = main_url + topic
    html_text = requests.get(url_topic).text
    soup = BeautifulSoup(html_text, 'html.parser')
    title = ''
    link = ''
    description = ''
    imageUrl = ''
    try:
        connection = mysql.connector.connect(host='localhost', database='news', user='root', password='Trongduc2206')
        # print(connection)
        cursor = connection.cursor();
        for article in soup.find_all('article'):
            if article.find('h2'):
                titleLink = article.find('h2').find('a')
                # if titleLink.get('title'):
                #     title = titleLink.get('title')
                # else :
                #     title = titleLink.text
                link = titleLink.get('href')
                select_sql = 'select * from news where news_key = %s'
                news_key_to_query = (link, )
                # news_key_to_query = ('https://vnexpress.net/quoc-hoi-se-xem-xet-bai-nhiem-ong-nguyen-thanh-long-4472897.html', )
                cursor.execute(select_sql, news_key_to_query)
                result = cursor.fetchone()
                # print(result)
                # break
                if result is None:
                    print('not exist')
                    sql = 'insert into news (title, topic_id_lv1, topic_id_lv2, topic_id_lv3, content, image_url, summary, pub_date, keyword, news_key, status, create_time, update_time) values (%s, 6, 52, 108, %s, %s, %s, %s, %s, %s, 1, now(), now() )'
                    # sql = 'insert into news (title, topic_id_lv1, topic_id_lv2, content, image_url, summary, pub_date, keyword, news_key, status, create_time, update_time) values (%s, 4, 38, %s, %s, %s, %s, %s, %s, 1, now(), now() )'
                    val = crawl(link)
                    print(val)
                    cursor.execute(sql, val)

                    connection.commit()
                    print("inserted 1 record with id", cursor.lastrowid)
                else:
                    print('this new existed')
                # break
                # sql = 'insert into news (title, topic_id, content, image_url, abstract, pub_date, keyword, news_key, status, create_time, update_time) values (%s, 15, %s, %s, %s, %s, %s, %s, 1, now(), now() )'
                # val = crawl(link)
                # print(val)
                # cursor.execute(sql, val)
                #
                # connection.commit()
                # print("inserted 1 record with id", cursor.lastrowid)

            # if article.find('p'):
            #     descriptionLink = article.find('p').find('a')
            #     description = descriptionLink.text
            #     if article.find('div', {'class':'thumb-art'}):
            #         image = article.find('div', {'class':'thumb-art'}).find('a').find('picture').find('img')
            #         imageUrl = image.get('src')
            #         print('Title: ' + title + " link " + link + " description " + description + " image url " + imageUrl)
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))


def crawl_topic():
    main_url = 'https://vnexpress.net/'
    html_text = requests.get(main_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    for li in soup.find_all('li'):
        print(li);

from pyvi import ViTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np


def similarity_cal(article_list, recommendNum):
# def similarity_cal():
#     text1 = get_article_text('https://vnexpress.net/nha-tuyen-dung-xay-dung-hinh-anh-thuong-hieu-the-nao-4476698.html')
#     text2 = get_article_text('https://vnexpress.net/gan-50-lao-dong-muon-chuyen-viec-sau-dich-4476124.html')
#     text3 = get_article_text('https://vnexpress.net/cong-nhan-mong-giam-tuoi-huu-hon-ha-nam-dong-bhxh-4475064.html')
#     text4 = get_article_text('https://vnexpress.net/lo-ngai-cong-nhan-khong-duoc-tang-luong-tu-1-7-4476920.html')
#     text5 = get_article_text('https://vnexpress.net/ngan-hang-nha-nuoc-se-tang-tan-suat-ban-ngoai-te-4478470.html')
#     trends = getRealtimeTrends()

    corpus = article_list
    # corpus = [text1, text2, text5, text3, text4]
    print(len(corpus))
    history_news_num = 10
    today_news_num = len(corpus) - history_news_num
    print("number of today news", today_news_num)

    stopwords = open('D:\\vietnamese-stopwords.txt', encoding="utf8").read().splitlines()
    vect = TfidfVectorizer(min_df=1, stop_words=stopwords)

    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T
    pairwise_similarity.toarray()
    points = []
    for x in range(today_news_num):

        point = 0

        for y in range(today_news_num, len(corpus)):
            point += pairwise_similarity[x, y]
        point = point / history_news_num
        print("point similar " + str(point))
        # print("point trend " + str(points_trend[x]))
        # overall_point = points_trend[x] * 0.2 + point * 0.8
        overall_point = point
        print("overall " + str(overall_point))
        points.append(overall_point)
    # print(pairwise_similarity[0, 1])

    print(pairwise_similarity)
    print(points)
    points_np = np.array(points)
    print(points_np)
    ind = np.argpartition(points_np, -recommendNum)[-recommendNum:]
    print(ind)
    # ind_list = ind.tolist()
    return ind.tolist()


def similarity_cal_single(article_list, recommendNum):
    corpus = article_list
    # corpus = [text1, text2, text5, text3, text4]
    print(len(corpus))
    history_news_num = 1
    today_news_num = len(corpus) - history_news_num
    print("number of today news", today_news_num)

    stopwords = open('D:\\vietnamese-stopwords.txt', encoding="utf8").read().splitlines()
    vect = TfidfVectorizer(min_df=1, stop_words=stopwords)

    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T
    pairwise_similarity.toarray()
    points = []
    for x in range(today_news_num):

        point = 0

        for y in range(today_news_num, len(corpus)):
            point += pairwise_similarity[x, y]
        point = point / history_news_num
        print("point similar " + str(point))
        # print("point trend " + str(points_trend[x]))
        # overall_point = points_trend[x] * 0.2 + point * 0.8
        overall_point = point
        print("overall " + str(overall_point))
        points.append(overall_point)
    # print(pairwise_similarity[0, 1])

    print(pairwise_similarity)
    print(points)
    points_np = np.array(points)
    print(points_np)
    ind = np.argpartition(points_np, -recommendNum)[-recommendNum:]
    print(ind)
    # ind_list = ind.tolist()
    return ind.tolist()


def similarity_cal_test():
    text1 = get_article_text('https://vnexpress.net/nha-tuyen-dung-xay-dung-hinh-anh-thuong-hieu-the-nao-4476698.html')
    text2 = get_article_text('https://vnexpress.net/gan-50-lao-dong-muon-chuyen-viec-sau-dich-4476124.html')
    corpus = [text1, text2]
    stopwords = open('D:\\vietnamese-stopwords.txt', encoding="utf8").read().splitlines()
    vect = TfidfVectorizer(min_df=1, stop_words=stopwords)
    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T
    pairwise_similarity.toarray()
    print(pairwise_similarity)
    text1_content = re.sub('\\n+', '</p><p>', '<p>' + text1 + '</p>')
    text2_content = re.sub('\\n+', '</p><p>', '<p>' + text2 + '</p>')
    corpus2 = [text1_content, text2_content]
    tfidf2 = vect.fit_transform(corpus2)
    pairwise_similarity2 = tfidf2 * tfidf2.T
    pairwise_similarity2.toarray()
    print(pairwise_similarity2)


if __name__ == '__main__':
    # res = crawl('https://vnexpress.net/ngay-dau-thu-phi-cang-bien-hon-8-ty-dong-4446845.html')

    crawl_list_by_topic('bong-da/bong-da-trong-nuoc')
    # crawl_topic()

    # print(res)

    # crawl_list_url();

    # connectDb()

    # print("----------------------------------------------------------------------")
    # process_keyword_rake('Lập Trình Không Khó là blog chia sẻ kiến thức lập trình miễn phí .Do vậy , tệp khách hàng của chúng tôi chủ yếu là đối tượng học lập trình , độ tuổi từ 18 - 24 và hầu hết là người dùng đến từ Việt Nam .Lập Trình Không Khó có hơn 300.000 người dùng trung bình mỗi tháng , đóng góp lượt xem trang trung bình mỗi ngày trên 20.000 views .Trong đó , trên 80 % lượng truy cập đến từ công cụ tìm kiếm ( Google , Cốc Cốc , ... ) .Ngoài ra , nhóm Lập Trình Không Khó trên Facebook hoạt động sôi nổi có tới 30.000 thành viên .')
    # process_keyword_rake('Lập trình không khó là một blog cá nhân của Nguyễn Văn Hiếu')
    # process_keyword_text_rank('Lập trình không khó là một blog cá nhân của Nguyễn Văn Hiếu')

    # process_key_word_yake('Lập trình không khó là một blog cá nhân của Nguyễn Văn Hiếu')
    # similarity_cal()
    # similarity_cal_test()
