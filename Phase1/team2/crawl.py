import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
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



club['League'] = league
club['Season'] = season
club = club.explode('Season').reset_index(drop=True)
club = club.assign(Club=np.NaN, ClubID=np.NaN, Squad=np.NaN, 
                   avgAge=np.NaN, Foreigners=np.NaN, avgMarketValue=np.NaN, 
                   totalMarketValue=np.NaN, Stadium=np.NaN, StadiumCap=np.NaN,
                   Club_income=np.NaN, Club_expenditure=np.NaN, Club_OverallBalance=np.NaN, 
                   Coach=np.NaN, Players=np.NaN)

club_table_league['League'] = league
club_table_league['Season'] = season
club_table_league = club_table_league.explode('Season').reset_index(drop=True)
club_table_league = club_table_league.assign(Club=np.NaN, Rank=np.NaN)


players = pd.DataFrame()
players['League'] = league
players['Season'] = season
players = players.explode('Season').reset_index(drop=True)
players.assign(ClubID=np.NaN, Player_name=np.NaN, Player_MarketValue=np.NaN, Player_possition=np.NaN)


for league, url in league_urls.items():
    for season in range(2015, 2022):
        page = requests.get(url + str(season), headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.content, 'html.parser')


        top_team = [team.text for team in soup.select("#yw4 .hauptlink a:nth-child(1)")] 
        club_table_league.loc[(club_table_league['Season'] == season) & (club_table_league['League'] == league), 'Club'] = ';'.join(top_team)
        club_table_league['Club'] = club_table_league['Club'].str.split(';')
        club_table_league = club_table_league.explode('Club').reset_index(drop=True)
        club_table_league.loc[(club_table_league['Season'] == season) & (club_table_league['League'] == league), 'Rank'] = [i + 1 for i in range(len(top_team))]
        
                                                  
        team = soup.select('#yw1 .no-border-links a:nth-child(1)')

        players.loc[(players['Season'] == season) & (players['League'] == league), 'ClubID'] = ';'.join(t.get('href').split("/")[-3] for t in team)
        players['ClubID'] = players['ClubID'].str.split(';')
        players = players.explode('ClubID').reset_index(drop=True)
        

        club.loc[(club['Season'] == season) & (club['League'] == league), 'Club'] = ';'.join(t.get('title') for t in team)
        club['Club'] = club['Club'].str.split(';')
        club.loc[(club['Season'] == season) & (club['League'] == league), 'ClubID'] = ';'.join(t.get('href').split("/")[-3] for t in team)
        club['ClubID'] = club['ClubID'].str.split(';')
        club = club.explode(['Club', 'ClubID']).reset_index(drop=True)
        

        squad = [squad.text for squad in soup.select(".no-border-links+ .zentriert > a")] 
        club.loc[(club['Season'] == season) & (club['League'] == league), 'Squad'] = squad
        
        age = [age.text for age in soup.select("#yw1 tbody .zentriert:nth-child(4)")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'avgAge'] = age
    
        foreigner = [number_Forigners.text for number_Forigners in soup.select("#yw1 tbody .zentriert:nth-child(5)")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'Foreigners'] = foreigner

        avrage_market_value = [market_value.text for market_value in soup.select("tbody .zentriert+ .rechts")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'avgMarketValue'] = avrage_market_value
 
        total_market_value = [total.text for total in soup.select("tbody .rechts+ .rechts")]
        club.loc[(club['Season'] == season) & (club['League'] == league), 'totalMarketValue'] = total_market_value
        
        club_urls = [link.get("href") for link in soup.select("#yw1 .no-border-links a:nth-child(1)")]
        for club_url in club_urls:
            club_id = club_url.split("/")[-3]
            club_page = requests.get("https://www.transfermarkt.com" + club_url, headers={'User-Agent': 'Mozilla/5.0'})  
            soup2 = BeautifulSoup(club_page.content, "html.parser")

            players_list = [player.text.split('.')[0][:-1] for player in soup2.select(".inline-table .hauptlink")]
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_name'] = ';'.join(players_list)
            players['Player_name'] = players['Player_name'].str.split(';')
            players = players.explode('Player_name').reset_index(drop=True)
            
            player_market_value = [pmv.text for pmv in soup2.select(".rechts.hauptlink")]
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_MarketValue'] = player_market_value
            
            player_main_possition = [possition.text for possition in soup2.select(".inline-table tr+ tr td")]
            players.loc[(players['ClubID'] == club_id) & (players['Season'] == season), 'Player_possition'] = player_main_possition
        

            stadium_name = [stadium.text for stadium in soup2.select(".data-header__items+ .data-header__items .data-header__label+ .data-header__label .data-header__content > a")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Stadium'] = stadium_name
            stadium_capacity = [capacity.text for capacity in soup2.select(".data-header__items+ .data-header__items .tabellenplatz")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'StadiumCap'] = stadium_capacity

            club_income = [income.text.replace("\n", "") for income in soup2.select(".transfer-record__total--positive")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_income'] = club_income
            
            club_expenditure = [Expenditure.text.replace("\n", "") for Expenditure in soup2.select(".transfer-record__total--negative")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_expenditure'] = club_expenditure

            club_OverallBalance = [Overall_balance.text.replace("\n", "").replace(' ','') for Overall_balance in soup2.select(".rechts.transfer-record__total")]
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Club_OverallBalance'] = club_OverallBalance

            coach_list = set(coach.text for coach in soup2.select(".staff-slider-main , .container-main > a"))
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Coach'] = ';'.join(coach_list)
            
            club.loc[(club['ClubID'] == club_id) & (club['Season'] == season), 'Players'] = ';'.join(players_list)


        print('\t',season, 'Done.')
    print(league,'Done.')



club.to_csv('club32.csv')
club_table_league.to_csv('club_table_league32.csv')
players.to_csv('players32.csv')
