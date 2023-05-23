import numpy as np
import requests
import pandas as pd
from bs4 import BeautifulSoup

data=[]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "accept-language": "en-US,en;q=0.9"}

all_players=pd.read_csv('All_players_links.csv')

for i in range(len((all_players))):
    p=all_players.iloc[i,0]
    id=p.split('spieler/')[-1]

    name=p.split('com/')[-1].split('/profil')[0]
    name=name.replace(' ','-')

    performance_link=f"https://www.transfermarkt.com/{name}/leistungsdaten/spieler/{id}/plus/0?saison=2021"
    page1=requests.get(performance_link, headers = headers)
    soup1 = BeautifulSoup(page1.content, "html.parser")


    appearances=np.nan
    goals=np.nan
    asists=np.nan
    yellow_cards=np.nan
    second_yellow_cards=np.nan
    red_cards=np.nan
    minutes_played=np.nan
    goals_conceded=np.nan
    clean_sheets=np.nan


    row={}
    if soup1.select('.empty'):
        pass
    else:
        x = soup1.select('#yw1 tfoot tr td')
        if len(x)==9:
            appearances=x[2].text
            goals = x[3].text
            asists = x[4].text
            yellow_cards = x[5].text
            second_yellow_cards = x[6].text
            red_cards = x[7].text
            minutes_played = x[8].text

        elif len(x)==10:
            appearances = x[2].text
            goals = x[3].text
            yellow_cards = x[4].text
            second_yellow_cards = x[5].text
            red_cards = x[6].text
            goals_conceded = x[7].text
            clean_sheets = x[8].text
            minutes_played = x[9].text


    row={'id':id,
    'name':name,
    'appearances':appearances,
    'goals':goals,
    'asists':asists,
    'yellow_cards':yellow_cards,
    'second_yellow_cards':second_yellow_cards,
    'red_cards':red_cards,
    'minutes_played':minutes_played,
    'goals_conceded':goals_conceded,
    'clean_sheets':clean_sheets}

    data.append(row)


player_stats=pd.DataFrame(data)
player_stats.to_csv('all_player_stats.csv',index=False)
