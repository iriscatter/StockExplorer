
#=========== pakages/modules that are used here ==============================
import en_core_web_sm
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
from os import path 
import pandas as pd

import stock_news as sn
import stock_twitter as sw

#================ code =======================================================
def create_wordcloud(text_str):
    '''
    Creates a word cloud image for a string containing a collectons of words
    
    Parameters
    ----------
    text_str(string): a string containing a collectons of words
    '''
    
    #set up word cloud
    nlp = en_core_web_sm.load()
    doc = nlp(text_str)
    
    newText =''
    for word in doc:
        if word.pos_ in ['ADJ', 'NOUN']:
            newText = " ".join((newText, word.text.lower()))
            
    wordcloud = WordCloud(width=1000, height=500,
                          collocations=False, stopwords = STOPWORDS
                          ).generate(newText)
    
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.figure(figsize=(6, 3), facecolor='k')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()


def create_news_worldcloud(ticker, pagenum):
    '''
    Creates a word cloud image for texts from news headlines
    
    Parameters
    ----------
    ticker(string): a stock ticker symbol
    
    pagenum(int): number of pages of news headlines a user wants to extract
    '''
    
    # news input file name
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_HisNews_' + today_str + '_p' + str(pagenum) +'.csv'  
    
    # if news input file N/A, extract and save news headlines for the stock 
    # first
    if path.exists(fint) == False:
        sn.get_stock_news(ticker, pagenum)
            
    # load the dataset 
    df = pd.read_csv(fint)
    
    # list comprehension to append all tweet text strings
    text_list = [i for i in df['Headline'] ]
    text_str = ''.join(text_list) 
    
    #create word cloud
    create_wordcloud(text_str)
    
   
def create_tweet_worldcloud(ticker):
    '''
    Creates a word cloud image for texts from Twitter
    
    Parameters
    ----------
    ticker(string): a stock ticker symbol
    '''
    
    date_today = datetime.today()
    today_str = date_today.strftime("%Y%m%d")
    fint = ticker + '_Tweets_' + today_str + '.csv' # twitter input file name
    
    # if twitter input file N/A, extract and save tweets for the stock first
    if path.exists(fint) == False:
        sw.collect_Tweet(ticker)
    
    # load twitter dataset 
    
    df = pd.read_csv(fint)
    # list comprehension to append all tweet text strings
    text_list = [i for i in df['Tweet Text'] ]
    text_str = ''.join(text_list) 
    
    #create word cloud
    create_wordcloud(text_str)
    
  

    