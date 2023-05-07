from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = "token"
client = WebClient(token=slack_token)

channel_id = "C056DNT4Y06"
links = [
    "https://www.trendyol.com/missha/su-bazli-nemlendirici-gunes-koruyucu-jel-50ml-all-around-safe-block-aqua-sun-gel-spf50-pa-p-4049713?boutiqueId=61&merchantId=104886&utm_source=share", 
]
driver = webdriver.Chrome(executable_path='chromedriver.exe')
ts = client.conversations_history(channel=channel_id)["messages"][0]['ts']

while True:
    time.sleep(1)
    last_text = client.conversations_history(channel=channel_id, oldest = ts)["messages"]
    if not last_text:
        continue
    else:
        ts = last_text[0]['ts']
    url = last_text[0]['text'][last_text[0]['text'].find('<')+1:last_text[0]['text'].find('>')]
    if "ty.gl" in url or "trendyol.com" in url:
        if url in links :
            response = client.chat_postMessage(channel=channel_id, text="This product is already in the check-list.")
            last_text = client.conversations_history(channel=channel_id, oldest = ts)["messages"]
            ts = last_text[0]['ts']
        else:
            response = client.chat_postMessage(channel=channel_id, text="Product is added to the check-list successfully!")
            last_text = client.conversations_history(channel=channel_id, oldest = ts)["messages"]
            ts = last_text[0]['ts']
            links.append(url)
    else:
        response = client.chat_postMessage(channel=channel_id, text="Your message does not include a Trendyol link.")
        last_text = client.conversations_history(channel=channel_id, oldest = ts)["messages"]
        ts = last_text[0]['ts']
    for link in links:
        time.sleep(1)
        driver.get(link)
        soup=BeautifulSoup(driver.page_source)
        buy_button = soup.find('button', {'class': 'add-to-basket'})
        if buy_button is not None:
            button_text = buy_button.text.strip()
            product_name = soup.find('h1', {'class': 'pr-new-br'})
            try:
                if button_text != 'Tükendi!':
                    response = client.chat_postMessage(channel=channel_id, text ="This product is now in stock: " + product_name.text.strip())
                    last_text = client.conversations_history(channel=channel_id, oldest = ts)["messages"]
                    ts = last_text[0]['ts']
                    print(f' This product is in stock: {product_name.text.strip()}')
                    links.remove(link)
            except:
                raise TypeError(f"Problem with button_text: {(button_text)}")
        else:
            print(f'Error occured for this link(probably can\'t find the button).')
            links.remove(link)
            print(link)