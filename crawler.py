import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv

page_num = 15
url = 'https://www.gamespot.com/games/reviews/'
url_list = [url,]
pages = []
soup_list = []
not_last_page = True
output_file = 'reviews.txt'
enum_state = 1

def pullUrl(func):
    def inner(*args, **kwargs):
        page = requests.get(url_list[-1])
        if page.status_code == 200:
            pages.append(page)
            func(*args, **kwargs)
        else:
            print(f'The url{url} returned a status of {page.status_code}')
        return inner

def makeSoup(func):
    def inner(*args, **kwargs):
        soup = BeautifulSoup(pages[-1].content, 'html.parser')
        soup_list.append(soup)
        func(*args, **kwargs)
    return inner

def soup_func():
    page = requests.get(url_list[-1])
    soup = BeautifulSoup(page.content, 'html.parser')
    soup_list.append(soup)
    print(soup_list)

# soup_func()
# @pullUrl
# def check_urls():
#     page = requests.get(url_list[-1])
#     for i in range(15, 6000):
#         print(f'The url{url} returned a status of {page.status_code}')


def getUrls(page_number=1):

    pages = f"{url}?page={page_number}"
    response = requests.get(pages)
    global enum_state

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        review_links = soup.select("div.card-item__content a[href]")
        if not review_links:
            return False

        with open(output_file, 'a', encoding='utf-8') as file:

            for link in review_links:
                print(f"{enum_state},https://www.gamespot.com{link['href']}")
                file.write(f"{enum_state},https://www.gamespot.com{link['href']},")
                file.write('\n')
                enum_state += 1

def aggregateText(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one("h1.kubrick-info__title")
    raw_title = title.get_text(strip=True)
    paragraphs = soup.find_all('p', attrs={"dir":"ltr"})

    results = " ".join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    return raw_title, results



def createDataframe():
    data_frame = []
    with open('reviews.csv', mode='r') as file:
        csv_reader = csv.reader(file)

        for line_num, row in enumerate(csv_reader, start=1):
            try:
                url = row[-1]
                print(f"Processing line {line_num}: {url}")
                
                res = aggregateText(url)
                if res[0] is None or res[1] is None:
                    print(f"Skipping line {line_num} due to errors.")
                    continue
                
                data_frame.append({"Title": res[0], "Content": res[1]})
            except Exception as e:
                print(f"Unexpected error on line {line_num}: {e}")

    df = pd.DataFrame(data_frame)
    df.to_csv('aggregated_reviews.csv', index=False)
    print(df)

createDataframe() 
