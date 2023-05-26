__author__ = "Zahra Honarvar, Milad Nooraei"
__email__ = "Zhpica@gmail.com, miladnooraiy0@gmail.com"
__mentor__ = "Diba Aminshahidi"
__organization__ = "Quera"
__date__ = "2023-05-24"

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np


def data_of_players(url, players_datas): 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "accept-language": "en-US,en;q=0.9"}     
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    res = {} 

    #Getting Players ID
    pattern = r"/(\d+)$"
    match = re.search(pattern, url)
    player_id = match.group(1)
    res["player_id"] = player_id

    #Getting Given Name and Shirt Number
    try:
        header = soup.find("h1", class_ = "data-header__headline-wrapper")
        shirt_number = header.find("span", class_ = "data-header__shirt-number").get_text(strip = True)
        given_name = " ".join(header.stripped_strings).replace(shirt_number, "").strip()
    except AttributeError:
        shirt_number = None
        given_name = None
    if given_name == None:
        try:
            given_name = soup.find("h1", class_ = "data-header__headline-wrapper").text.strip()
        except AttributeError:
            given_name = None
    res["shirt_number"] = shirt_number
    res["given_name"] = given_name

    #Getting Full Name
    try:
        full_name = soup.select_one("span.info-table__content.info-table__content--bold").get_text(strip = True)
        pattern = r"\d+"
        match = re.search(pattern, full_name)
        if(bool(match)):
            full_name = None
    except AttributeError:
        full_name = None
    res["full_name"] = full_name

    #Getting Date Of Birth
    try:
        date_of_birth = soup.select_one("span.info-table__content.info-table__content--bold a[href^='/aktuell/waspassiertheute/aktuell/new/datum/']").text.strip()
    except AttributeError:
        date_of_birth = None
    res["date_of_birth"] = date_of_birth

    #Getting Citizenship
    try:
        citizenship = soup.select_one("li.data-header__label span[itemprop='nationality']").get_text(strip = True)
    except AttributeError:
        citizenship = None
    res["citizenship"] = citizenship

    #Getting Place Of Birth
    try:
        place_of_birth = soup.select_one("li.data-header__label span.data-header__content[itemprop='birthPlace']").get_text(strip = True)
    except AttributeError:
        place_of_birth = None
    res["place_of_birth"] = place_of_birth

    #Getting Caps and Goals
    try:
        caps = soup.select_one("li.data-header__label > a:nth-of-type(1).data-header__content--highlight").get_text(strip = True)
        goals = soup.select_one("li.data-header__label > a:nth-of-type(2).data-header__content--highlight").get_text(strip = True)
    except AttributeError:
        caps = None
        goals = None
    res["caps"] = caps
    res["goals"] = goals

    #Getting Player Agent
    try:
        agent = soup.select_one("li.data-header__label:contains('Agent') a").get_text(strip = True)
    except AttributeError:
        agent = None

    #Getting Other Positions
    try:
        other_position_soup = soup.find("div", class_ = "detail-position__position")
        other_positions = [position.text.strip() for position in other_position_soup.find_all("dd", class_ = "detail-position__position")]
        other_positions = ", ".join(other_positions)
    except AttributeError:
        other_positions = None
    res["other_positions"] = other_positions

    temp = soup.select("#main > main > div > div.large-8.columns > div > div > div.large-6.large-pull-6.small-12.columns.spielerdatenundfakten > div > span")

    outfitter = None
    contract_expires = None
    foot = None
    contract_Joined = None
    height = None
    current_club = None
    date_of_last_contract = None

    for i in range(len(temp)):
        #Getting Outfitter
        if "Outfitter" in temp[i].text:
            outfitter = temp[i+1].text.strip()
        #Getting Contract Expires
        elif "Contract expires" in temp[i].text:
            contract_expires = temp[i+1].text.strip()
        #Getting Agent
        elif "agent" in temp[i].text and agent == None:
            agent = temp[i+1].text.strip()
        #Getting Foot
        elif "Foot" in temp[i].text:
            span = temp[i+1].text.strip()
            if span == 'right' or span == 'left' or span == 'both':
                foot = span
        #Getting Joined
        elif "Joined" in temp[i].text:
            contract_Joined = temp[i+1].text.strip()
        #Getting Height
        elif "Height" in temp[i].text:
            height = temp[i+1].text.strip()
            height = str("".join(filter(str.isdigit, height)))
        #Getting Current Club
        elif "Current club" in temp[i].text:
            current_club = temp[i+1].text.strip()
        #Getting last Contract
        elif "last contract" in temp[i].text:
            date_of_last_contract = temp[i+1].text.strip()

    res["outfitter"] = outfitter
    res["contract_expires"] = contract_expires
    res["agent"] = agent
    res["foot"] = foot
    res["contract_Joined"] = contract_Joined
    res["height"] = height
    res["current_club"] = current_club
    res["date_of_last_contract"] = date_of_last_contract
 
    return res


def players_transfer_table(url):  
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "accept-language": "en-US,en;q=0.9"}     
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    #Getting Transfer Data
    try:
        transfer_table = soup.find("div", {"data-viewport" : "Transferhistorie"})
        rows = transfer_table.find_all("div", class_ = "grid tm-player-transfer-history-grid")
        transfer_table_list = []
        for i in rows:
            clean_text = i.text.strip()
            lines = clean_text.split("\n")
            lines = [line.strip() for line in lines if line.strip()]
            if ("2017" in lines[1]) or ("2018" in lines[1]) or ("2019" in lines[1]) or ("2020" in lines[1]) or ("2021" in lines[1]):
                transfer_table_list += [lines]
        return transfer_table_list
    
    except AttributeError:
        pass


def player_stats_table(url, name):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "accept-language": "en-US,en;q=0.9"}     
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

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
    if soup.select('.empty'):
        pass
    else:
        x = soup.select('#yw1 tfoot tr td')
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

    return row

    

links = 'https://www.transfermarkt.com' + pd.read_csv("data/players_link.csv")

cols = ["player_id", "shirt_number", "given_name", "full_name", "date_of_birth",
        "citizenship", "place_of_birth", "caps", "goals", "other_positions", 
        "outfitter", "contract_expires", "agent", "foot", "contract_Joined",
        "height", "current_club", "date_of_last_contract", "players_link"]
players_datas = pd.DataFrame(columns=cols).astype(str)

cols=["player_id", "season", "date", "left", "joined", "mv", "fee"]
transfer_table = pd.DataFrame(columns=cols).astype(str)


for i in range(len(links)):
    #---players_datas
    res1 = data_of_players(links.loc[i, "0"], players_datas)
    # players_datas = players_datas.append(res1, ignore_index = True) # for pandas==1.3.4
    players_datas = pd.concat([players_datas, pd.DataFrame([res1])], ignore_index=True)

    #---players_transfers
    res2 = {}
    #Getting Players ID
    pattern = r"/(\d+)$"
    match = re.search(pattern, links.loc[i, "0"])
    player_id = match.group(1)
    table_list = players_transfer_table(links.loc[i, "0"])
    
    for j in table_list:
        if len(j) == 6:
            res2["player_id"] = player_id
            res2["season"] = j[0]
            res2["date"] = j[1]
            res2["left"] = j[2]
            res2["joined"] = j[3]
            res2["mv"] = j[4]
            res2["fee"] = j[5]
            # transfer_table = transfer_table.append(res2, ignore_index = True) # for pandas==1.3.4
            transfer_table = pd.concat([transfer_table, pd.DataFrame([res2])], ignore_index=True)
    
    #---players_stats
    player_stats = []
    p=links.iloc[i,0]
    id=p.split('spieler/')[-1]
    
    name=p.split('com/')[-1].split('/profil')[0]
    name=name.replace(' ','-')
    performance_link=f"https://www.transfermarkt.com/{name}/leistungsdaten/spieler/{id}/plus/0?saison=2021"

    res3 = player_stats_table(performance_link, name)
    player_stats.append(res3)

    print(f'player{i} Done.')



pd.DataFrame(players_datas).to_csv("data/players_datas.csv", index = False)
pd.DataFrame(transfer_table).drop_duplicates().to_csv("data/players_transfers.csv", index = False)
pd.DataFrame(player_stats).to_csv('data/players_stats.csv',index=False)