import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_content(url):
    response = requests.get(url)
    
   
    soup = BeautifulSoup(response.text, 'html.parser')
        
    title = soup.find('h1')
    title_text = title.text
        
        
    content_divs1 = soup.find_all('div', class_='td-post-content tagdiv-type')
        
        
        
    content_divs2 = soup.find_all('div', class_='tdb-block-inner td-fix-index')

        

        
    for content_div1 in content_divs1:
            for pre_tag in content_div1.find_all('pre', class_='wp-block-preformatted'):
                pre_tag.extract()

            content_text1 = content_div1.get_text(separator='\n')
    
    for content_div2 in content_divs2:
            for pre_tag in content_div2.find_all('pre', class_='wp-block-preformatted'):
                pre_tag.extract()

            content_text2 = content_div2.get_text(separator='\n')


    return title_text, content_text1, content_text2
    


excel_file_path = 'Input.xlsx'
df = pd.read_excel(excel_file_path)


for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    
    print(f"\nScraping content for URL_ID {url_id} - {index + 1}/{len(df)}\n")
    
    title, article_text1, article_text2 = scrape_content(url)
    
    if title is not None and article_text1 is not None and article_text2 is not None:
        file_name = f"{url_id}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"{title}\n")
            file.write(article_text1)
            file.write(article_text2)
        print(f"Article text saved to {file_name}\n")
