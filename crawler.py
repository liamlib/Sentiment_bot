import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv
import bs4
import json

page_num = 15
url = 'https://www.gamespot.com/games/reviews/'
url_list = [url,]
pages = []
soup_list = []
not_last_page = True
output_file = 'reviews.txt'
enum_state = 1


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

    title = soup.select_one("h1.kubrick-info__title") or soup.select("h1.news-title.instapaper_title.entry-title")[0]
    raw_title = title.get_text(strip=True)
    rating = soup.select_one("div.review-ring-score__score.text-bold").get_text(strip=True)

    headers = soup.find_all('h4') #Headers for pros and cons  ("The Good" or "The Bad")

    pros_list_text = ["The Good", "the good", "The good"]
    cons_list_text = ["the bad", "The bad", "The Bad"]
    pros_list = []
    cons_list = []

    for header in headers: 
        if header.get_text(strip=True) in pros_list_text:
            pros = header.find_next_sibling()
            if pros and pros.name in ['ul', 'ol']:
                pros_list = [li.get_text(strip=True) for li in pros.find_all('li')]
            else:
                print("No list found below this header.")
        elif header.get_text(strip=True) in cons_list_text:
            cons = header.find_next_sibling()
            if cons and cons.name in ['ul', 'ol']:
                cons_list = [li.get_text(strip=True) for li in cons.find_all('li')]
            else:
                print("No list found below this header.")
            
    paragraphs = soup.find_all('p', attrs={"dir":"ltr"}) or soup.find("div", class_="js-content-entity-body").find_all('p')
    results = " ".join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    return raw_title, results, rating, pros_list, cons_list


def createDataframe():
    failed_links = []
    output_file = 'aggregated_reviews_2.json'
    
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json_file.write('[\n')

    with open('reviews.csv', mode='r') as file:
        csv_reader = csv.reader(file)

        for line_num, row in enumerate(csv_reader, start=3471):
            try:
                url = row[-1]
                print(f"Processing line {line_num}: {url}")
                
                res = aggregateText(url)
                if res[0] is None or res[1] is None:
                    print(f"Skipping line {line_num} due to errors.")
                    continue

                record = {
                    "Index": line_num,
                    "Title": res[0],
                    "Content": res[1],
                    "Rating": res[2],
                    "Pros": res[3],
                    "Cons": res[4]
                }

                with open(output_file, 'a', encoding='utf-8') as json_file:
                    json.dump(record, json_file, ensure_ascii=False)
                    json_file.write(',\n')
            except Exception as e:
                failed_links.append({"Line": line_num, "URL": row[-1], "Error": str(e)})
                print(f"Unexpected error on line {line_num}: {e}")

    with open(output_file, 'rb+') as json_file:
        json_file.seek(-2, 2)
        json_file.truncate()
        json_file.write(b'\n]')

    if failed_links:
        failed_df = pd.DataFrame(failed_links)
        failed_df.to_csv('failed_links.csv', index=False)
        print("Saved failed links to 'failed_links.csv' successfully!")
    else:
        print("No failed links.")

createDataframe() 
