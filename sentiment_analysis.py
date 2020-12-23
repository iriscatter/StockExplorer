
#=========== pakages/modules that are used here ==============================
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer


#================ code =======================================================
def getSubjectivity(text):
    '''
    Gets the subjectivity score from a text input
    
    Parameters
    ----------
    text(string): a text string
        
    Returns
    -------
    returns a number ranging from 0 to 1, where 
    0 = objective, 1 = subjective
    '''
    return TextBlob(text).sentiment.subjectivity


def getPolarity(text):
    '''
    Gets the polarity from a text input
    
    Parameters
    ----------
    text(string): a text string
        
    Returns
    -------
    returns a number ranging from 0 to 1, where 
    1 = positive, -1 = negative, 0 = neutral
    '''
    return TextBlob(text).sentiment.polarity


def getSIA(text):
    '''
    Gets the sentiment scores (using Sentiment Intensity Analyzer) from a text 
    input.
    
    Parameters
    ----------
    text(string): a text string
        
    Returns
    -------
    returns a dictionary that contains negative, positive, neutral, compound 
    scores.
    
    compound score is a normalized value.
    '''
    
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment