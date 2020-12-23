#=========== pakages/modules that are used here ==============================
import re
import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta
from os import path 
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import statsmodels.api as sm

import stock_price as sp
import sentiment_analysis as sa

#================ code =======================================================
def clean_tweet_text(tweet): 
    '''
    Cleans a tweet text by removing @mentions, hashtags, replies, any empty
    lines, and hyperlink.
    
    Parameters
    ----------
    tweet(string): a twitter tweet
        
    Returns
    -------
    Returns a cleaned tweet text.
    '''
    tweet = re.sub(r'@[A-Za-z0-9]+','', tweet)  # remove @mentions
    tweet = re.sub(r'#', '', tweet)  # Remove '#' hash tag
    tweet = re.sub(r'RT [@:]', '', tweet) # remove RT
    tweet = re.sub(r'\n', '', tweet) # remove an empty line
    tweet = re.sub('https?://[A-Za-z0-9./]+','', tweet)  # remove hyperlink
    
    return tweet
    

def collect_tweet(ticker):
    '''
    Import tweets about a stock over past 8 days, up to 200 tweets per day.
    Save the cleaned the tweets as a csv file.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns twitter output's csv file name.
    '''
    # output file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fout = ticker + '_Tweets_' + today_str + '.csv'
    
    # if output file already exists, stop and return the filename
    if path.exists(fout) == True:
        return fout
    
    # add your Tweeter API key info 
    consumerKey=''
    consumerSecret = ''
    accessToken =''
    accessTokenSecret =''
    
    # set up the authentication object
    auth = tw.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tw.API(auth, wait_on_rate_limit = True)
    
    # Collect tweets with keyword, English language for the past 8 days
    search_word = ticker + " " + sp.get_co_short_name(ticker)  #keywords
    tweets_list = []
    
    # search up to 200 tweets per day, for past 8 days
    for i in range(0, 8):
        date_until = datetime.today() - timedelta(days= i)
        date_until_str = date_until.strftime("%Y-%m-%d")  #end date for search
        
        date_since = date_until - timedelta(days= 1)
        date_since_str = date_since.strftime("%Y-%m-%d") #start date for search
        
        # collect tweets up to 200 tweets per day
        tweets = tw.Cursor(api.search,
                            q = search_word,
                            lang = "en",
                            since = date_since_str,
                            until = date_until_str,
                            result_type = "mixed",
                            tweet_mode = 'extended').items(200)
   
        for tweet in tweets:
            #tweet date
            tweet_date = tweet.created_at.strftime("%Y-%m-%d")
            
            #get full text
            if tweet.truncated == True:
                full_tweet_text = tweet.retweeted_status.full_text
            else:
                full_tweet_text = tweet.full_text
            
            #clean text
            clean_text = clean_tweet_text(full_tweet_text)
            tweets_list.append([tweet_date, clean_text])
    
    # save in a panda Dataframe
    df = pd.DataFrame(tweets_list,  columns = ['Date','Tweet Text']) 
    
    # save in csv
    df.to_csv(fout, index = False, encoding='utf-8-sig')
    
    return fout


def calc_twitter_sa(ticker):
    '''
    Calculates sentiment score for all stock tweets, and add the scores(positive, 
    negative, neutral, compound) as 4 new columns to the original csv file
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns twitter output's csv file name.
    '''
    
    # output file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_Tweets_' + today_str + '.csv'
    
    # if twitter file N/A, collect tweets first.
    if path.exists(fint) == False:
        collect_tweet(ticker)
    
    #load tweet data
    df = pd.read_csv(fint)
    
    # if a column called 'Compound' already exists in the file, return the file
    # name and stop.
    # because it means sentiment scores have been added.
    if 'Compound' in df.columns:
        return fint
    
    # Get the sentiment scores for each trading day
    compound = []   # compound score
    neg = []        # negative score
    neu = []        # neutral score
    pos = []        # positive score
    
    # calculate compound, negative, neutral, positive for each day by loop
    for i in range(0, len(df['Tweet Text'])):
        SIA = sa.getSIA(df['Tweet Text'][i])
        compound.append(SIA['compound'])
        neg.append(SIA['neg'])
        neu.append(SIA['neu'])
        pos.append(SIA['pos'])
          
    #store the sentiment scores in the data frame
    df['Compound'] = compound
    df['Negative'] = neg
    df['Neutral'] = neu
    df['Positive'] = pos
    
    #save in csv
    df.to_csv(fint, index = False, encoding='utf-8-sig')
    
    return fint



def merge_twitter_price(ticker):
    '''
    Merges tweet sentiment score with stock price during the past 8 days.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns the merged DataFrame that contains data, stock price and tweet
    sentiment score (compound score).
    '''
    date_today = datetime.today()
    from_date = date_today - timedelta(days = 8)
    today_str = date_today.strftime("%Y-%m-%d")     #today's date
    from_date_str = from_date.strftime("%Y-%m-%d")  #date that is 8 days ago

    #tweet file name
    fint_1 = ticker + '_Tweets_' + today_str.replace('-','') + '.csv'
    
    #stock price file name, where from_date is 8 days ago, and to_date is today.
    fint_2 = ticker + '_HisPrice_' + from_date_str.replace('-','') +\
                         '_' + today_str.replace('-','') + '.csv' 
                         
    print("\n    loading tweets about " + ticker +" ... (this can take a while)")
    #collect tweets and calculate sentiment scores if tweet file N/A
    if path.exists(fint_1) == False:
        calc_twitter_sa(ticker)   
    
    #get stock price if price file N/A
    if path.exists(fint_2) == False:
        sp.load_stock_price(ticker, from_date_str, today_str)
        
    #add price movement direction and change in % for the price file
    sp.add_price_move(ticker, from_date_str,today_str)
        
    #load twitter data
    df_twitter = pd.read_csv(fint_1, index_col = 0)
    # get average Compound score by date and save it as a new DataFrame
    df_twitter_new = df_twitter.groupby(['Date']).agg({'Compound':'mean',
                                                       })    
    
    #load price data
    df_price = pd.read_csv(fint_2, index_col = 0)
    
    # inner join by date
    df_twitter_price= df_price.merge(df_twitter_new, how = 'inner', on ='Date', 
                                     left_index = True)
    
    return df_twitter_price


def plot_twitter_sa_price(ticker):
    '''
    Plots tweet sentiment score vs stock price movement over the past 8 days
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    '''
    
    # gets the merged data about tweet sentiment and price over the past 8 days
    df = merge_twitter_price(ticker)
    
    # convert index from text to date type
    df.index = pd.to_datetime(df.index)

    # create graph
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # plot price change percentage over time
    ax.set_xlabel('Date').set_size(10)
    ax.set_ylabel('Closing Price', color = 'brown')
    
    # bar chart for price change in %
    ax.bar(df.index, df['PriceChg'], color = 'lightsalmon', label='Price Change %' )
  
    # plot polarity score percentage over time on a secondary y-axis
    ax2 = ax.twinx()
    ax2.plot(df.index, df['Compound'], color = 'royalblue',label='Compound Score')
    ax2.set_ylabel('Compound Score', color ='royalblue')  
    
    # set axis limit and format labels/ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    ax.set_title(ticker.upper() +" - price change% vs tweets' sentiment").set_size(10)
    ax.tick_params(axis= "x", labelsize = 8)
    ax.tick_params(axis= "y", labelsize = 8)
    ax2.tick_params(axis= "y", labelsize = 8)
    
    # display one single legend when there is multiple y-axis
    handles,labels = [],[]
    for ax in fig.axes:
        for h,l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)
    
    plt.legend(handles,labels, loc = 2, prop={'size': 8})
    
    fig.tight_layout()
    plt.show()
    

def model_tweet_sa_price(ticker):
    '''
    Analyzes the significance of tweet sentiment score on stock price 
    during the past 8 days.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    '''
    
    # load the merged dataset that contains price and tweet sentiment scores
    df = merge_twitter_price(ticker)
    
    #pick opening price, Compound score, Polarity scores as x variables
    X = df[['Open','Compound']] 
    
    #pick adj close price as outcome variable
    Y = df['Adj Close']
    X = sm.add_constant(X) # adding a constant
     
    #assign OLS model
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
     
    #print model summary
    print_model = model.summary()
    print(print_model)
    
    # plot 
    mpl.rcParams.update(mpl.rcParamsDefault)
    df.index = pd.to_datetime(df.index)
    
    fig, ax = plt.subplots(figsize=(6, 3))
    
    #plot actual stock price
    ax.plot(df.index, Y.values, '-', color = 'royalblue', label = 'actual closing price')
    
    #plot model stock price
    ax.plot(df.index, predictions , '--*', color = 'darkorange', label = 'model closing price')
    
    # format labels and ticks
    ax.set_ylabel('Price').set_size(10)
    ax.set_xlabel('Date').set_size(10)
    ax.tick_params(axis = "x", labelsize = 8 ,  rotation = 0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.tick_params(axis = "y", labelsize = 8 )
    ax.set_title(ticker +': Actual closing price vs OLS Model price').set_size(10)
    plt.legend(loc=4, prop={"size":8})
    plt.tight_layout()
    plt.show()
    

def plot_twitter_sa(ticker):
    '''
    Creates a plot that displays a stock's tweets' sentiment score
    movement over the past 8 days
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    '''
    
    # tweet output file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_Tweets_' + today_str + '.csv'
    
    print("\n    loading tweets about " + ticker + " ... (this can take a while)")
    
    #collect tweets and calculate sentiment score if tweet file N/A
    if path.exists(fint) == False:
        calc_twitter_sa(ticker)
        
    # load tweet dataset
    df = pd.read_csv(fint)
    
    # get average Positive, Negative, Neutral, Compound score, group by Date
    df_meanSA = df.groupby(['Date']).agg({'Positive':'mean', 
                                         'Negative':'mean',
                                         'Neutral':'mean',
                                         'Compound':'mean'})

    # change the Date text format from yyyy-mm-dd to mm-dd
    df_meanSA.index = pd.Series([i[-5:] for i in df_meanSA.index ])
    
    # create plots
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax2 = ax.twinx()  #add a secondary y-axis
    
    # creates a stacked bar plot with y-axis from the left for 3 scores,
    # because Positive + Negative + Neutral = 100%
    df_meanSA[['Positive', 'Negative', 'Neutral']].plot(ax =ax, kind='bar', 
        stacked=True, color=['forestgreen', 'firebrick', 'darkgrey'])
    
    # creates a separate compound score plot with y-axis from the right
    df_meanSA[['Compound']].plot(ax = ax2, kind='line', label='Compound', 
                                color = 'royalblue', )
    
    
    # prevent separate legends from displaying
    ax.get_legend().remove()
    ax2.get_legend().remove()
    
    #format tickers
    ax.tick_params(axis = "x", labelsize = 8 , rotation = 0)
    ax.tick_params(axis = "y", labelsize = 8 )
    ax2.tick_params(axis = "y", labelsize = 8, colors = 'royalblue' )
    
    #format titles and labels
    ax.set_xlabel('Date').set_size(8)
    ax.set_ylabel('Pos/Neg/Neu Score')
    ax2.set_ylabel('Compound Score', color = 'royalblue')
    ax.set_title(ticker + ': ' + 'Tweets Sentiment Score Movement').set_size(10)
    
    # display one single legend when there is multiple y-axis
    handles,labels = [],[]
    for ax in fig.axes:
        for h,l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)
    
    plt.legend(handles,labels, loc = 2, prop={'size': 8})
    fig.tight_layout()
    plt.show()

def plot_multi_tweet_sa(ticker_list):
    '''
    Plots multiple stocks' tweet sentiment score movement over the past 8 
    days
    
    Parameters
    ----------
    ticker_list(list): a list containing up to 5 tickers
    '''
    
    # line styles for each different stocks (up to 5 stocks in a plot)
    all_linestyles = [':*', '-', '--', '-.', ':' ]
    used_linestyles = all_linestyles [ : len(ticker_list)]
    
    # loop each ticker to get average sentiment compound score by date
    # and then join all in one Dataframe
    for i in range(len(ticker_list)):
        ticker = ticker_list[i]
       
        date_today = datetime.today()
        today_str = date_today.strftime("%Y%m%d")
        fint = ticker + '_Tweets_' + today_str + '.csv'   # input file name
        
        # if input file N/A, extract tweets and calc sentiment score
        # for the stock first
        print("\n    loading tweets about " + ticker +" ... (this can take a while)")
        if path.exists(fint) == False:
            collect_tweet(ticker)
        calc_twitter_sa(ticker)
        
        # load the stock's tweets dataset that contains sentiment compound scores
        df_ticker_i = pd.read_csv(fint)
        df_ticker_i = df_ticker_i[['Date', 'Compound']]
            
        #rename 'Compound'' column to ticker
        df_ticker_i = df_ticker_i.groupby(['Date'])['Compound'].mean().reset_index().round(decimals=4) 
        df_ticker_i.rename(columns={'Compound': ticker}, inplace = True)
    
        
        # merge DataFrame
        if i == 0:
            pd_merge_tweet = df_ticker_i
        else:
            pd_merge_tweet = pd_merge_tweet.merge(df_ticker_i, how = 'inner', on ='Date', 
                                                  left_index = True)
            
    # convert Date from string to date type
    pd_merge_tweet['Date'] = pd.to_datetime(pd_merge_tweet['Date'])
    
    # change Date from column to index
    pd_merge_tweet.set_index('Date',inplace = True)
    
    # plot sentiment scores for all tickers 
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # loop to add plots one by one with unique line styles
    for i, j in zip(pd_merge_tweet.columns, used_linestyles ):
        ax.plot(pd_merge_tweet.index, pd_merge_tweet[i].values, j)
    
    # format labels and ticks
    ax.set_xlim(min(pd_merge_tweet.index), max(pd_merge_tweet.index))
    ax.tick_params(axis = "x", labelsize = 8 )
    ax.tick_params(axis = "y", labelsize = 8 )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    
    ax.set_ylabel('Sentiment Score').set_size(10)
    ax.set_xlabel('Date').set_size(10)
    ax.set_title("Tweet sentiment score over time").set_size(10)
    plt.legend(ticker_list, loc =2,  prop={"size":8})
    plt.tight_layout()
    plt.show()
    

