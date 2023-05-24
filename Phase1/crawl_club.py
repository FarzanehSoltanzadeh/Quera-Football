__author__ = "Farzaneh Soltanzadeh, Ali Mousavi"
__email__ = "f.soltanzadeh.f@gmail.com, ali.mousavi4878@gmail.com"
__mentor__ = "Diba Aminshahidi"
__organization__ = "Quera"
__date__ = "2023-05-24"

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

""" 
England : 189
Germany: 40
Italy: 75
France : 50
Spain : 157
URL : https://www.transfermarkt.com/wettbewerbe/national/wettbewerbe/{CountryID}
"""

club = pd.DataFrame([{'CountryID': 189, 'Country': 'England'},
        {'CountryID': 40, 'Country': 'Germany'},
        {'CountryID': 75, 'Country': 'Italy'},
        {'CountryID': 50, 'Country': 'France'},
        {'CountryID': 157, 'Country': 'Spain'}])

club_table_league = pd.DataFrame()


league = []
for i in range(len(club)):
    url = f"https://www.transfermarkt.com/wettbewerbe/national/wettbewerbe/{club.loc[i,'CountryID']}"
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    league.append(soup.select('.inline-table a')[1].get('title'))

league_urls = {'Premier League': 'https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=',
               'Bundesliga': 'https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1/plus/?saison_id=',
               'Serie A': 'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1/plus/?saison_id=',
               'Ligue 1': 'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1/plus/?saison_id=',
               'LaLiga': 'https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1/plus/?saison_id='}

season = [[i for i in range(2015, 2022)] for j in range(len(club))]
All_Players_Link = []


club['League'] = league
club['Season'] = season
club = club.explode('Season').reset_index(drop=True)
club = club.assign(Club=np.NaN, ClubID=np.NaN, Squad=np.NaN, 
                   avgAge=np.NaN, Foreigners=np.NaN, avgMarketValue=np.NaN, 
                   totalMarketValue=np.NaN, Stadium=np.NaN, StadiumCap=np.NaN,
                   Club_income=np.NaN, Club_expenditure=np.NaN, Club_OverallBalance=np.NaN, 
                   Coach=np.NaN, Club_victories=np.NaN, Players=np.NaN)


club_table_league['League'] = league
club_table_league['Season'] = season
club_table_league = club_table_league.explode('Season').reset_index(drop=True)
club_table_league = club_table_league.assign(Club=np.NaN, Rank=np.NaN)


players = pd.DataFrame()
players['League'] = league
players['Season'] = season
players = players.explode('Season').reset_index(drop=True)
players.assign(ClubID=np.NaN, Player_name=np.NaN, PlayerID=np.NaN, Player_MarketValue=np.NaN, Player_possition=np.NaN)


for league, url in league_urls.items():
    for season in range(2015, 2022):
        page = requests.get(url + str(season), headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.content, 'html.parser')

        # add Rank and Club name columns to club_table_league dataFrame
        top_team = [team.text for team in soup.select("#yw4 .hauptlink a:nth-child(1)")] 
        club_table_league.loc[(club_table_league['Season'] == season) & (club_table_league['League'] == league), 'Club'] = ';'.join(top_team)
        club_table_league['Club'] = club_table_league['Club'].str.split(';')
        club_table_league = club_table_league.explode('Club').reset_index(drop=True)
        club_table_league.loc[(club_table_league['Season'] == season) & (club_table_league['League'] == league), 'Rank'] = [i + 1 for i in range(len(top_team))]
        
        # get Clubs                                         
        team = soup.select('#yw1 .no-border-links a:nth-child(1)')
        
        # add ClubID to players dataFrame
        players.loc[(players['Season'] == season) & (players['League'] == league), 'ClubID'] = ';'.join(t.get('href').split("/")[-3] for t in team)
        players['ClubID'] = players['ClubID'].str.split(';')
        players = players.explode('ClubID').reset_index(drop=True)
        
        # add ClubID and Club name to club dataFrame
        club.loc[(club['Season'] == season) & (club['League'] == league), 'Club'] = ';'.join(t.get('title') for t in team)
        club['Club'] = club['Club'].str.split(';')
        club.loc[(club['Season'] == season) & (club['League'] == league), 'ClubID'] = ';'.join(t.get('href').split("/")[-3] for t in team)
        club['ClubID'] = club['ClubID'].str.split(';')
        club = club.explode(['Club', 'ClubID']).reset_index(drop=True)
        
        # add Squad column to club dataFrame 
        squad = [squad.text for squad in soup.select(".no-border-links+ .zentriert > a")] 
        club.loc[(club['Season'] == season) & (club['League'] == league), 'Squad'] = squad
        
        # add aveAge to club dataFrame 
        age = [age.text for age in soup.select("#yw1 tbody .zentriert:nth-child(4)")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'avgAge'] = age
    
        # add foreigner count to club dataFrame 
        foreigner = [number_Forigners.text for number_Forigners in soup.select("#yw1 tbody .zentriert:nth-child(5)")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'Foreigners'] = foreigner

        # add avgMarketValue to club dataFrame 
        avrage_market_value = [market_value.text for market_value in soup.select("tbody .zentriert+ .rechts")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'avgMarketValue'] = avrage_market_value

        # add totalMarketValue to club dataFrame 
        total_market_value = [total.text for total in soup.select("tbody .rechts+ .rechts")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'totalMarketValue'] = total_market_value
        
        # trace on the players page
        club_urls = [link.get("href") for link in soup.select("#yw1 .no-border-links a:nth-child(1)")]
        for club_url in club_urls:
            club_id = club_url.split("/")[-3]
            club_page = requests.get("https://www.transfermarkt.com" + club_url, headers={'User-Agent': 'Mozilla/5.0'})  
            soup2 = BeautifulSoup(club_page.content, "html.parser")

            # get all players from the club
            players_list = soup2.select(".inline-table .hauptlink .hide-for-small > a")
            # get all players url from the club
            All_Players_Link.extend(p.get('href') for p in players_list)
            
            # add player name and player id to player dataFrame
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_name'] = ';'.join(p.text for p in players_list)
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'PlayerID'] = ';'.join(p.get('href').split('/')[-1] for p in players_list)
            players['Player_name'] = players['Player_name'].str.split(';')
            players['PlayerID'] = players['PlayerID'].str.split(';')
            players = players.explode(['Player_name', 'PlayerID']).reset_index(drop=True)

            # add player Market Value to player dataFrame
            player_market_value = [pmv.text for pmv in soup2.select(".rechts.hauptlink")]
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_MarketValue'] = player_market_value
            
            # add player possition to player dataFrame
            player_main_possition = [possition.text for possition in soup2.select(".inline-table tr+ tr td")]
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_possition'] = player_main_possition
        
            # add stadium name and stadium capacity to club dataFrame
            stadium_name = [stadium.text for stadium in soup2.select(".data-header__items+ .data-header__items .data-header__label+ .data-header__label .data-header__content > a")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Stadium'] = stadium_name
            stadium_capacity = [capacity.text for capacity in soup2.select(".data-header__items+ .data-header__items .tabellenplatz")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'StadiumCap'] = stadium_capacity

            # add club income to club dataFrame
            club_income = [income.text.replace("\n", "").replace(' ','') for income in soup2.select(".transfer-record__total--positive")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_income'] = club_income
            
            # add club expenditure to club dataFrame
            club_expenditure = [Expenditure.text.replace("\n", "").replace(' ','') for Expenditure in soup2.select(".transfer-record__total--negative")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_expenditure'] = club_expenditure

            # add club overallBalance to club dataFrame
            club_overallBalance = [Overall_balance.text.replace("\n", "").replace(' ','') for Overall_balance in soup2.select(".rechts.transfer-record__total")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_OverallBalance'] = club_overallBalance

            # add coach name to club dataFrame
            coach_list = set(coach.text for coach in soup2.select(".staff-slider-main , .container-main > a"))
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Coach'] = ';'.join(coach_list)
            
            # add players name to club dataFrame
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Players'] = ';'.join(p.text for p in players_list)

            # add club victories to club dataFrame
            champoin = [champion.get("href") for champion in soup2.select(".data-header__badge-container > a")]
            if not champoin:
                continue
            
            champoin_page = requests.get("https://www.transfermarkt.com" + champoin[0], headers={'User-Agent': 'Mozilla/5.0'})
            soup3 = BeautifulSoup(champoin_page.content, "html.parser")
            
            champoin_list = [ch.text for ch in soup3.select("td:nth-child(1) , .no-border-links")]
            victories = []
           
            for i in range(0, len(champoin_list), 2):
                year, name = champoin_list[i].split('/')[0], champoin_list[i+1]
                if len(year) == 2 and 1 <= int(year[0]) <= 2:
                    if int('20' + year) == season:
                        victories.append(name)
            
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_victories'] = ';'.join(victories)
     
            
        print('\t',season, 'Done.')  
    print(league,'Done.')

   

club.to_csv('data/club.csv')
club_table_league.to_csv('data/club_table_league.csv')
players.to_csv('data/club_players.csv')
pd.DataFrame(All_Players_Link).drop_duplicates().to_csv("data/players_link.csv", index = False)
