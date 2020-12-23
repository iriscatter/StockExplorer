
#=========== pakages/modules that are used here ==============================
#import from Python standard modules
import colored
from colored import stylize
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from os import path 
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib import style

#import from the modules I have created
import stock_price as sp
import sentiment_analysis as sa

#================ code =======================================================
# text printing styles for alert messages
invalid_style = colored.fg("red") + colored.attr("bold")


def get_stock_news(ticker, pagenum):    
    '''
    Web scrape a stock's news headlines from 'Business Insider' website, and 
    save the data in a csv, given number of pages of news headlines a user wants
    extract.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    pagenum(int): number of pages of news headlines a user wants to extract
        
    Returns
    -------
    Returns the csv output file name.
    
    for example: if the ticker is AMZN, today is Dec 12 2020, and pagenum = 30.
    output file name = 'AMZN_HisNews_20201212_p30.csv'
    '''
    cur_time = datetime.now()   #current time
    all_news = []               # create an empty list to store news headlines
    
    # output file name 
    fout = ticker + '_HisNews_' + cur_time.strftime('%Y%m%d') +\
            '_p' + str(pagenum) +'.csv'
            
    # if output file already exists, just return the filename
    if path.exists(fout) == True:
        return fout
    
    # loop news webpage one by one to web scrape the news headlines
    for i in range(1, pagenum + 1):
        url='https://markets.businessinsider.com/news/{}?p={}'.format(ticker.lower(),
                                                                      str(i))
        req = requests.get(url)
        
        #check if a url exists/works
        if req.status_code == 200:
            soup = BeautifulSoup(req.content, 'lxml')
            newsSoup = soup.find_all('div', 
                                     {"class": "col-md-6 further-news-container latest-news-padding"})
            
            for j in range(len(newsSoup)):
                #news headline text
                news_title = newsSoup[j].find('a').get_text()
                
                #elapsed time since the news headline has been posted
                news_time_section = newsSoup[j].find('span', 
                                                     {"class": "warmGrey source-and-publishdate"}
                                                     ).get_text()
                news_time = news_time_section.split()[-1]
                
                # the measurement unit of elapsed time: m (minutes), h (hours) or d (days)
                time_unit = news_time[-1]
                
                # get the amount of elapsed time in the measurement unit
                time_amount = int(news_time[:-1].replace(',', ''))
                
                #compare the current time and the elapsed time to get the date
                #when the news was posted
                if time_unit == 'm': 
                    news_date = cur_time - timedelta(minutes = time_amount)
                elif time_unit == 'h': 
                    news_date = cur_time - timedelta(hours = time_amount)
                elif time_unit == 'd': 
                    news_date = cur_time - timedelta(days = time_amount)
            
                # convert the new post date to yyyy-mm-dd text string
                news_date = news_date.strftime('%Y-%m-%d')
                
                #append the news to the news list
                all_news.append([news_date, news_title])
        
    # store all news in panda Dataframe and sace as csv
    news_df = pd.DataFrame(all_news, columns=['Date', 'Headline'])   
    news_df.to_csv(fout, index = False, encoding = 'utf-8-sig')
 
    return fout

def calc_news_sa(ticker, pagenum):
    '''
    Calculate each piece of news headline's sentiment scores regarding
    subjectivity, polarity, compound, positivity, negativity, neutrality.
    
    Add all these sentiment scores (6 columns) to the news csv file.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    pagenum(int): number of pages of news headlines a user wants to extract
        
    Returns
    -------
    a panda Dataframe for news, with all those sentiment scores added.
    '''
    
    #news file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_HisNews_' + today_str + '_p' + str(pagenum) +'.csv'  
    
    # if news fint N/A, extract and save stock news first
    print("\n    loading news about " + ticker +" ...")
    if path.exists(fint) == False:
        get_stock_news(ticker, pagenum)
    
    df = pd.read_csv(fint)      #load news data
    
    # if a column called 'Subjectivity' already exists in the news file, stop 
    # and returns the file name.
    # beccause it means all sentiment scores have been added to the file.
    if 'Subjectivity' in df.columns:
        return df
        
    # Get subjectivity and polarity for news headline
    df['Subjectivity'] = df['Headline'].apply(sa.getSubjectivity)
    df['Polarity'] = df['Headline'].apply(sa.getPolarity)
    
    # Get the sentiment scores for each day
    compound = []   # compound score
    neg = []        # negative score
    neu = []        # neutral score
    pos = []        # positive score
    
    # loop to calculate compound, negative, neutral, positive for each day 
    for i in range(0, len(df['Headline'])):
        SIA = sa.getSIA(df['Headline'][i])
        compound.append(SIA['compound'])
        neg.append(SIA['neg'])
        neu.append(SIA['neu'])
        pos.append(SIA['pos'])
      
    # store the sentiment scores as columns in the DataFrame
    df['Compound'] = compound
    df['Negative'] = neg
    df['Neutral'] = neu
    df['Positive'] = pos

    #save the updated DataFrame to the news csv file.
    df.to_csv(fint, index = False, encoding='utf-8-sig')
    
    return df


def display_news_10(ticker, pagenum):
    '''
    Displays the most recent 10 news headlines for a stock.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    pagenum(int): number of pages of news headlines a user wants to extract
    '''
    # news input file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_HisNews_' + today_str + '_p' + str(pagenum) +'.csv'
    
    # if news fint N/A, extract and save stock news first
    print("\n    loading news about " + ticker +" ...")
    if path.exists(fint) == False:
        calc_news_sa(ticker, pagenum)
    
    # load the most recent 10 news headlines
    df = pd.read_csv(fint).head(10)
    
    # print the most recent 10 news headlines
    print('''
     Index  Date         Headlines
     -----  ----------   ---------''')
     
    for index, row in df.iterrows():
        print('     ' + '{:^5s}'.format(str(index+1)) +'  {:>10s}'.format(row['Date']) + 
              '   ' + '{:<s}'.format(row['Headline']))
        
        
def merge_news_sa_price(ticker, from_date, pagenum):
    '''
    Merge stock news sentiment scores (Compound and Polarity) with stock 
    price data.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    from_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    pagenum(int): number of pages of news headlines a user wants to extract
    
    Returns
    -------
    a merged panda Dataframe that contains price info and news sentiment scores.
    '''
    
    # news input file name
    # date_today = datetime.today() - timedelta(days = 1)
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint_news = ticker + '_HisNews_' + today_str + '_p' + str(pagenum) +'.csv'  
    
    # stock price input file name
    end_date = date_today.strftime('%Y-%m-%d')  
    fint_price = ticker + '_HisPrice_' + from_date.replace('-','') +\
                '_' + end_date.replace('-','') + '.csv' 
                         
    # if news file N/A, extract and save stock news
    # otherwise, load stock news data
    if path.exists(fint_news) == False:
        df_news  = calc_news_sa(ticker, pagenum)
    else:
        df_news = pd.read_csv(fint_news, index_col = 0)
        
    # get avergae Compound and Polarity score by date for news headlines
    df_news_new = df_news.groupby(['Date']).agg({'Compound':'mean', 
                                             'Polarity':'mean'})    
         
    # if price file N/A, extract and save stock price
    if path.exists(fint_price) == False:
        # if there is no price data between the from_date to today, 
        # returns -1 and stop
        if sp.load_stock_price(ticker, from_date, end_date) == False:
            return -1
        
        #add price movement direction and change in % to the stock price data
    sp.add_price_move(ticker, from_date, end_date)
        
    # load stock price data
    df_price = pd.read_csv(fint_price, index_col = 0)
    
    # inner join stock price and news sentiment by date
    df_price_news = df_price.merge(df_news_new, how = 'inner', on ='Date', 
                                   left_index = True)
    
    return df_price_news


def model_news_sa_price(ticker, from_date, pagenum):
    '''
    Analyzes the significance of the news headlines sentiments on the stock 
    price movement day over day, by using OLS model
    
    Display the OLS model summary and a plot about sentiment movement vs price 
    movement
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    from_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    pagenum(int): number of pages of news headlines a user wants to extract
    '''
    # load the merged dataset between price and news sentiment
    df = merge_news_sa_price(ticker, from_date, pagenum)
    
    # if there is price data between the from_date to today, returns -1 and stop
    if type(df) != pd.DataFrame:
        return -1
    
    # stop if the data size is too little
    if len(df) <= 3:
        print(stylize('    Not enough price or news data to display. Try again.', 
                      invalid_style))
        
        return -1
    
    #pick opening price, Compound score, Polarity scores as x variables
    X = df[['Open','Compound', 'Polarity']] 
    
    #pick adj close price as outcome variable
    Y = df['Adj Close']
    
    X = sm.add_constant(X) # adding a constant
     
    #assign OLS model
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
     
    #print model summary
    print_model = model.summary()
    print(print_model)
    
    # plot sentiment scores for all tickers 
    mpl.rcParams.update(mpl.rcParamsDefault) #set plot format back to default 
    df.index = pd.to_datetime(df.index)      #convert index from string to date type
    fig, ax = plt.subplots(figsize=(6, 3))
    
    #plot actual stock price
    ax.plot(df.index, Y.values, '-', color = 'royalblue', label = 'Real Price')
    
    #plot model stock price
    ax.plot(df.index, predictions , '--*', color = 'darkorange',
                                        label = 'Model Price')
    # format labels and ticks
    ax.set_ylabel('Price').set_size(10)
    ax.set_xlabel('Date').set_size(10)
    ax.tick_params(axis = "x", labelsize = 8 ,  rotation = 0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.tick_params(axis = "y", labelsize = 8 )
    ax.set_title(ticker +': Real stock price vs OLS Model price').set_size(10)
    plt.legend(loc=2, prop={"size":8})
    plt.tight_layout()
    plt.show()




def plot_news_sa_price(ticker, from_date, pagenum):
    '''
    Plots a stock's news headlines' sentiment movement vs price movement
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    from_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    pagenum(int): number of pages of news headlines a user wants to extract
    '''
    # get df with merged news sentiment and price history
    df_price_news = merge_news_sa_price(ticker, from_date, pagenum)

    #if there is no data between from_date and today, return -1 and stop.
    if type(df_price_news) != pd.DataFrame:
        return -1
    
    # returns -1 if data size is too small
    if len(df_price_news) <= 3:
        print(stylize('    Not enough price or news data to display. Try again.', 
                      invalid_style))
        return -1
    
    # convert index from text to date type
    df_price_news.index = pd.to_datetime(df_price_news.index)
    
    # plot price change in % vs Polarity score
    x_date = df_price_news.index
    y_price = df_price_news['PriceChg']
    y_score = df_price_news['Polarity']
    
    # create graph
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(111)
    
    # plot price change percentage over time
    ax.set_xlabel('Date').set_size(10)
    ax.set_ylabel('Price Chg %', color = 'brown')
    lns1 = ax.plot(x_date, y_price, color = 'brown', label='Price Chg %' )
 
    # plot polarity score over time on a secondary y-axis
    ax2 = ax.twinx()
    lns2 = ax2.plot(x_date, y_score, color = 'royalblue',label='Polarity Score')
    ax2.set_ylabel('Polarity Score', color ='royalblue')  
    
    # set axis limit
    ax.set_ylim(min(y_price) *1.1, max(y_price)*1.1)
    ax2.set_ylim(min(y_score)*1.1, max(y_score)*1.1)
    ax.set_xlim(min(x_date), max(x_date))
    
    # format labels and ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.set_title('Price Change% vs News Sentiment Score').set_size(10)
    ax.tick_params(axis="x", labelsize = 8)
    ax.tick_params(axis="y", labelsize = 8)
    ax2.tick_params(axis="y", labelsize = 8)
    
    # merge legends
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc = 2, prop={'size': 8})
    fig.tight_layout()
    plt.show()



def plot_mutli_news_sa(ticker_list, pagenum):
    '''
    Plots several stocks' news headlines polarity score movement during a period
    
    Parameters
    ----------
    ticker_list(list): a list containing up to 5 tickers
    
    pagenum(int): number of pages of news headlines a user wants to extract
    '''
    
    # create an empty panda DataFrame
    pd_merge_news = pd.DataFrame()
    
    # loop each ticker to get historical price info
    # then merge their 'Adj Close' column by date
    for i in range(len(ticker_list)):
        ticker = ticker_list[i]
        
        #load Dataframe about a stock's news with its sentiment scores
        df_news_i = calc_news_sa(ticker, pagenum)  
        
        # get avergae Polarity score by date for news headlines
        df_news_i = df_news_i.groupby(['Date']).agg({'Polarity':'mean'})    
        
        #rename 'Polarity' column to 'Polarity - ticker'
        df_news_i.rename(columns={'Polarity': 'Polarity - ' + ticker}, inplace = True)
        
        # merge DataFrame by date
        if i == 0:
            pd_merge_news = df_news_i
        else:
            pd_merge_news = pd_merge_news.merge(df_news_i, how = 'inner', on ='Date', 
                                                left_index = True)
    
    # convert index from string to date type
    pd_merge_news.index = pd.to_datetime(pd_merge_news.index)
    
    # plot Polarity movements for all tickers 
    mpl.rcParams.update(mpl.rcParamsDefault)
    style.use("ggplot")
    
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # line styles for each different stock
    all_linestyles = [':*', '-', '--', '-.', ':' ]
    used_linestyles = all_linestyles [ : len(ticker_list)]
    
    # loop to add plots one by one with unique line styles
    for i, j in zip(pd_merge_news.columns, used_linestyles ):
        ax.plot(pd_merge_news.index, pd_merge_news[i].values, j)
    
    # format labels and ticks
    ax.tick_params(axis="x", labelsize = 8)
    ax.tick_params(axis="y", labelsize = 8)
    ax.set_xlim(min(pd_merge_news.index), max(pd_merge_news.index))
    ax.set_ylabel('News Polarity Score').set_size(8)
    ax.set_xlabel('Date').set_size(8)
    ax.set_title('News Polarity Score Comparison').set_size(10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.legend(ticker_list, loc = 2, prop={"size":8})
    fig.tight_layout()
    plt.show()




