import requests
import json
import pandas
import re
from bs4 import BeautifulSoup

def checkTitle(title, semcore):
    res = False
    for word in semcore:
        a = re.search(word.lower(), title.lower())
        res |= a
    return res

        

def checkTitles(df, semcore):
    titles = df['Title']
    df['Rescheck'] = np.nan
    for i, title in enumerate(titles):
        df['Rescheck'][i] = checkTitle(title)
    return df




if __name__ == "__main__":

    api_key = "AIzaSyCksnTwknw5Da4F4_7VZqgUYe32_TkaEFw"

    response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&q=камчатка&type=video&videoCaption=closedCaption&key={api_key}').json()
    print(response)
    

    semcore = ['камчат', 'эко']