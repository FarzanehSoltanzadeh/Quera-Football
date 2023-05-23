import numpy as np
import requests
from bs4 import BeautifulSoup


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "accept-language": "en-US,en;q=0.9"}

url = "https://www.transfermarkt.com/ruben-loftus-cheek/profil/spieler/202886"#test
url="https://www.transfermarkt.com/mikel-john-obi/profil/spieler/30739"#test

page = requests.get(url, headers = headers)
soup = BeautifulSoup(page.content, "html.parser")


id=url.split('spieler/')[-1].split('/plus')[0]


temp=soup.select('#main > main > div > div.large-8.columns > div > div > div.large-6.large-pull-6.small-12.columns.spielerdatenundfakten > div > span')

Outfitter=np.NAN
Contract_expires=np.NAN
agent=np.NAN
foot=np.NAN
contract_Joined=np.NAN
Height=np.NAN
Current_club=np.NAN
Date_of_last_contract=np.NAN


for i in range(len(temp)):
    if 'Outfitter'in temp[i].text:
        Outfitter=temp[i+1].text.strip()

    elif 'Contract expires'in temp[i].text:
        Contract_expires = temp[i + 1].text.strip()

    elif 'agent'in temp[i].text:
        agent = temp[i + 1].text.strip()

    elif 'Foot'in temp[i].text:
        foot = temp[i + 1].text.strip()

    elif 'Joined'in temp[i].text:
        contract_Joined = temp[i + 1].text.strip()

    elif 'Height'in temp[i].text:
        Height = temp[i + 1].text.strip()

    elif 'Current club'in temp[i].text:
        Current_club = temp[i + 1].text.strip()

    elif 'last contract'in temp[i].text:
        Date_of_last_contract = temp[i + 1].text.strip()