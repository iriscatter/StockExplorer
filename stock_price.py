
#=========== pakages/modules that are used here ==============================
import requests, time, re, string
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib import style
from os import path 
import colored
from colored import stylize
#================ code =======================================================
# text printing styles for alert messages
invalid_style = colored.fg("red") + colored.attr("bold")

def get_co_full_name(ticker):
    '''
    Gets a company's name based on a ticker symbol'
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns the company's name if the ticker is valid.
    Otherwise, returns False.
    '''
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker)
    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == ticker:
            return x['name']
    
    return False

def get_co_short_name(ticker):
    '''
    Gets the first word from a company's name, given a ticker.
    
    For example, if a company's name is 'Amazon.com, Inc.', the function returns
    'Amazon' since it is the first word from the name.
    
    The function will be used for searching tweets about a company through 
    keyword.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
        
    Returns
    -------
    Returns the first word (string) from a company's full name.
    '''
    co_fullname = get_co_full_name(ticker)
    co_name_split = re.split("[" + string.punctuation + " ]+", co_fullname)
    return co_name_split[0]


def format_date(date_text):
    '''
    Converts a date text like yyyy-mm-dd to an integer that an url can 
    understand.
    
    The function is used when extracting historical stock prices from yahoo
    finance hidden API.
    
    Parameters
    ----------
    date_text(string): a date in the text form like yyyy-mm-dd
        
    Returns
    -------
    Returns an integer that represents a date in an url link.
    '''
    format_date = datetime.strptime(date_text, '%Y-%m-%d')
    date_timetuple = format_date.timetuple()
    date_mktime = time.mktime(date_timetuple)
    date_int = int(date_mktime)
    date_str = str(date_int)
    return date_str


def load_stock_price(ticker, start_date, end_date): 
    '''
    Saves a stock's historical prices as a csv file, given a start and end date.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    start_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    end_date(string): a string that means the end date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    Returns
    -------
    Returns a text, which means the output file name.
    
    Returns False, if there is no price data between the given start and end
    dates.
    '''
    
    # output file name
    f_name = ticker + '_HisPrice_' + start_date.replace('-','') + \
             '_' + end_date.replace('-','') + '.csv'
    
    # if outpout file exists, stop
    if path.exists(f_name) == True:
        return f_name
    
    # convert dates to a proper integer that an url can understand
    start_date_str = format_date(start_date)
    end_date_str = format_date(end_date)
    
    # stock price url
    stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?'.format(ticker)
    
    #stock url's paramter
    price_param ={
        'period1': start_date_str,
        'period2': end_date_str,
        'interval' :'1d',
        'events':'history'}
    
    #load the historical data
    response = requests.get(stock_url, params = price_param)
    
    # if there is no stock price between 2 dates (when date duration is too short)
    if response.text == '404 Not Found: Timestamp data missing.' or\
       "400 Bad Request: Data doesn't exist for" in response.text:
        
        print (stylize('\n    There is no data between these 2 dates. Try again.',
                           invalid_style))
        return False
    else:
        #save the historical data as a csv file
        f = open(f_name, "w")
        f.write(response.text) 
        f.close()
        
        return f_name
  
    
def add_price_move(ticker, start_date, end_date):
    '''
    add 2 more columns to indicate the stock price movements and change
    percentage day over day in its csv output file
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    start_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    end_date(string): a string that means the end date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    Returns
    -------
    Returns a text, which means the output file name if 2 columns can be added.
    
    Reurns -1, if there is no price data between the given start and end dates.
    '''
    
    # csv file that stores price history
    f_name = ticker + '_HisPrice_' + start_date.replace('-','') + \
             '_' + end_date.replace('-','') + '.csv'
    
    # if there is no price data between the given start and end dates,
    # returns -1
    if path.exists(f_name) == False:
        if load_stock_price(ticker, start_date, end_date) == False:
            return -1
        
    #open the price history csv file
    df_price = pd.read_csv(f_name, index_col=0)
    
    # if a column called 'PriceDir' exists in the csv file, just stop and return
    # the csv file name.
    # because it means the 2 columns have been added.
    if 'PriceDir' in df_price.columns:
        return f_name
        
    # create a list to store price movement direction day over day, where
    #   -1 means price goes down, 0 means no change, and 1 means price goes up
    price_dir = []
    
    # create a list to store price change in percentage day over day
    price_chg = []
    
    for i in range(0, len(df_price['Adj Close'])):
        # first row of the price, mark both price movement direction and change
        # in percentage as 0.
        if i == 0:
            price_dir.append(0)
            price_chg.append(0)
        else:
            pre_price = df_price['Adj Close'].iloc[i-1]  #previous day's price
            cur_price = df_price['Adj Close'].iloc[i]    #current day's price
        
            #append the price movement direction to the price_dir list
            if cur_price > pre_price:
                price_dir.append(1)
                
            elif cur_price < pre_price:
                price_dir.append(-1)
            else:
                price_dir.append(0)
            
            #append the price change in % to the price_chg list
            price_chg.append((cur_price - pre_price)/ pre_price * 100)
            
    # add 2 columns called 'PriceDir' and 'PriceChg' in the DataFrame to 
    # represent the price movement direction and change in %
    df_price['PriceDir'] = price_dir
    df_price['PriceChg'] = price_chg
    
    # save the updated DataFrame as a csv file, with the same file name.
    df_price.to_csv(f_name, encoding = 'utf-8')
    
    return f_name

 
def plot_price_volm(ticker, start_date, end_date):
    '''
    Plots a stock's Adj Close Price and Trading Volume movement as 2 subplots 
    in one big plot.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    start_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    end_date(string): a string that means the end date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    Returns
    -------
    Reurns -1, if there is no price data between the given start and end dates.
    '''
    
    # set plot format back to default 
    mpl.rcParams.update(mpl.rcParamsDefault)
    style.use("ggplot")
    
    # stock price file name
    fint = ticker + '_HisPrice_' + start_date.replace('-','') +\
           '_' + end_date.replace('-','') + '.csv'
    
    # if there is no price data between the given start and end dates,
    # returns -1
    if path.exists(fint) == False:
        if load_stock_price(ticker, start_date, end_date) == False:
            return -1
    
    #load price data
    df_price = pd.read_csv(fint)
    
    if len(df_price) <= 3:
        print (stylize('\n    There is no data to display. Try again.',
                           invalid_style))
        return False
    
    # convert date from string to date type
    df_price['Date'] = pd.to_datetime(df_price['Date'])
    
    # create 2 subplots
    plt1 = plt.subplot2grid((4,4), (0, 0), rowspan = 3, colspan = 4)
    plt2 = plt.subplot2grid((4,4), (3,0), rowspan = 1, colspan = 4, sharex= plt1)
    
    plt1.plot(df_price['Date'], df_price["Adj Close"], color='royalblue') 
    plt2.fill_between(df_price['Date'], df_price['Volume'].values, 0, color='royalblue')
    
    plt1.axes.get_xaxis().set_visible(False) #hide top graph's x-axis
    plt2.set_xlim(min(df_price['Date']), max(df_price['Date'])) #set x-axis limit
    
    #set labels
    plt1.set_title(ticker + ' - closing price and trading volume').set_size(10)
    plt1.set_ylabel('Adj Closing Price').set_size(10)
    plt2.set_ylabel('Volume').set_size(10)
    plt2.set_xlabel('Date').set_size(10)
    plt1.tick_params(axis = "x", labelsize = 8 , rotation = 0)
    plt1.tick_params(axis = "y", labelsize = 8 )
    plt2.tick_params(axis = "x", labelsize = 8 , rotation = 0)
    plt2.tick_params(axis = "y", labelsize = 8 )
    plt2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    #set size and space
    plt.gcf().set_size_inches(6,3)
    plt.tight_layout(pad=0.2, w_pad=0.5, h_pad=0.1)
    plt.show()


def plot_sma(ticker, start_date, end_date):
    '''
    Plots a stock's price simple moving averages(SMA) during a given start
    and end dates.
    
    Parameters
    ----------
    ticker(string): a ticker symbol
    
    start_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    end_date(string): a string that means the end date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    Returns
    -------
    Reurns -1, if there is no price data between the given start and end dates.
    '''
    
    mpl.rcParams.update(mpl.rcParamsDefault) #set plot format back to default 
    style.use("ggplot")
    
    # stock price file name
    fint = ticker + '_HisPrice_' + start_date.replace('-','') +\
            '_' + end_date.replace('-','') + '.csv'
    
    # if there is no price data between the given start and end dates,
    # returns -1
    if path.exists(fint) == False:
        if load_stock_price(ticker, start_date, end_date) == False:
            return -1
    
    #load price data
    df_price = pd.read_csv(fint)   
    
    if len(df_price) <= 3:
        print (stylize('\n    There is no data to display. Try again.',
                           invalid_style))
        return False
    
    
    # convert date from string to date type
    df_price['Date'] = pd.to_datetime(df_price['Date'])
    
    # create simple moving average for every 10, 20 or 50 days
    sma10 = df_price['Adj Close'].rolling(10).mean() #10 days
    sma20 = df_price['Adj Close'].rolling(20).mean() #20 days
    sma50 = df_price['Adj Close'].rolling(50).mean() #50 days
    
    
    #create a Dataframe to store moving average related data
    df_MA = pd.DataFrame({'Date': df_price['Date'],
                          'Adj Close': df_price['Adj Close'],
                          'SMA 10': sma10, 
                          'SMA 20': sma20, 
                          'SMA 50': sma50})
    
    # convert 'Date' column as index
    df_MA.set_index('Date',inplace = True)
    
    # plot
    ax = df_MA.plot(figsize=(6, 3), legend = True, 
               color = {'Adj Close': 'brown',
                        'SMA 10':'seagreen' ,
                        'SMA 20':'mediumblue',
                        'SMA 50':'darkorange',})
    
    #format labels and ticks
    ax.set_title(ticker + " - simple moving average over time").set_size(10)
    ax.set_ylabel('Price').set_size(10)
    ax.set_xlabel('Date').set_size(10)
    ax.tick_params(axis = "x", labelsize = 8 , rotation = 0)
    ax.tick_params(axis = "y", labelsize = 8 )
    plt.legend(loc =2, prop={"size":8})
    plt.tight_layout()
    plt.show()



def plot_multi_price(ticker_list, start_date, end_date):
    '''
    Plots several stocks' price movement during a period
    
    Parameters
    ----------
    ticker_list(list): a list containing up to 5 tickers
    
    start_date(string): a string that means the start date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    end_date(string): a string that means the end date for a stock's 
    price inquiry, with format like yyyy-mm-dd
    
    Returns
    -------
    Reurns -1, if there is no price data between the given start and end dates.
    '''
    
    # create an empty panda DataFrame
    pd_merge_price = pd.DataFrame()
    
    
    # loop each ticker to get historical price info
    # then merge their 'Adj Close' column by date
    for i in range(len(ticker_list)):
        ticker = ticker_list[i]                               # ticker symbol
        fint = load_stock_price(ticker, start_date, end_date) # price file name
        
        # if there is no price data between the given start and end dates,
        # returns -1 and stop
        if fint == False:
            return -1
        
        # load price data
        df_price_i = pd.read_csv(fint)
        
        if len(df_price_i) <= 3:
            print (stylize('\n    There is no data to display. Try again.',
                           invalid_style))
            return False
    
    
        df_price_i = df_price_i[['Date', 'Adj Close']]
        
        #rename 'Adj Close' column to their ticker symbol
        df_price_i.rename(columns={'Date': 'Date', 'Adj Close': ticker},
                          inplace=True)
        
        # merge Dataframe by their Date column
        if i == 0:
            pd_merge_price = df_price_i
        else:
            pd_merge_price = pd_merge_price.merge(df_price_i, how = 'inner', on ='Date', 
                                                  left_index = True)
    
    # convert Date from string to date type
    pd_merge_price['Date'] = pd.to_datetime(pd_merge_price['Date'])
    
    # change Date from column to index
    pd_merge_price.set_index('Date',inplace = True)
    
    
    
    
    
    # plot price movements for all tickers 
    mpl.rcParams.update(mpl.rcParamsDefault) #set plot format back to default 
    style.use("ggplot")
    
    ax = pd_merge_price.plot(figsize=(6, 3), legend = True)
    
    #format labels and ticks
    ax.set_xlim(min(pd_merge_price.index), max(pd_merge_price.index))
    ax.set_title('Adj Close Price Movement Comparison').set_size(10)
    ax.set_ylabel('Adj Close Price').set_size(10)
    ax.set_xlabel('Date').set_size(10)
    ax.tick_params(axis = "x", labelsize = 8 )
    ax.tick_params(axis = "y", labelsize = 8 )
    plt.legend(loc = 2, prop={"size":8})
    plt.tight_layout()
    plt.show()
        
