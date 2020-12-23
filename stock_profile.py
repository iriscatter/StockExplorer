
#=========== pakages/modules that are used here ==============================
import pandas as pd
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from os import path 

#================ code =======================================================
def get_co_stat(ticker):
    '''
    Gets a company's basic profile from a ticker input
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns profile file output name.
    '''
    
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fout = ticker + '_Stats_' + today_str +'.csv'   #output file name
    
    # if output file already exits, returns the file name and stop.
    if path.exists(fout) == True:
        return fout
    
    #web scrapes the company's profile from finviz
    url = "http://finviz.com/quote.ashx?t={}".format(ticker.lower())
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = soup(webpage, "lxml")
    
    stat_info = {}
    stat_info['Sector'] =""
    stat_info['Industry'] =""
    stat_info['Country'] =""

    try:
        # find sector, industry and contry info
        profile_soup = html.find_all('td', {"class": "fullview-links"})
        profile_info = profile_soup[1].find_all('a', {"class": "tab-link"})
    
        for i in range(len(profile_info)):
            if i == 0:
                stat_info['Sector'] = profile_info[i].text
            elif i == 1:
                stat_info['Industry'] = profile_info[i].text
            elif i == 2:
                stat_info['Country'] = profile_info[i].text
    

        # find the stat_table table
        stat_table = pd.read_html(str(html), 
                                  attrs = {'class': 'snapshot-table2'}
                                  )[0]
        
    
        # append stat term and result to stat_info list
        for i in np.arange(0, 6, 2):
            for j in np.arange(0, 6):
                stat_term = stat_table.iloc[j][i]
                term_result = stat_table.iloc[j][i+1]
                stat_info[stat_term] = term_result
        
        # convert stat_info list to DataFrame
        stat_pd = pd.DataFrame(stat_info.items(), columns=['Attributes', 'Values'])
        
        #save in csv
        stat_pd.to_csv(ticker + '_Stats_' + today_str +'.csv', index = False, 
                       encoding='utf-8-sig')
    
    except Exception as e:
        return e        
    
def display_profile(ticker):
    '''
    Displays a company's basic profile in a nice format
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    '''
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fout = ticker + '_Stats_' + today_str +'.csv'  #profile input file name
    
    #if profile input file N/A, web scrape the profile info and save first
    if path.exists(fout) == False:
        get_co_stat(ticker)
        
    df = pd.read_csv(fout)  #load profile data
    
    #print profile in a nice format
    print('''
      Attributes   Values
     -----------   ------''')
    
    for index, row in df.iterrows():
        print('     ' + '{:>11s}'.format(row['Attributes']) + 
              '   ' + '{:<20s}'.format(row['Values']))
    

