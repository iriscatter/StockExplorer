
#=========== pakages/modules that are used here ==============================
import colored
from colored import stylize
from datetime import datetime, timedelta

import stock_profile as sf
import stock_price as sp
import stock_twitter as st
import stock_news as sn
import word_cloud as wc

#================ code =======================================================
# my company name
myCompanyName = 'Stock Scanner'

# main menu
main_menu = {}
main_menu['1'] = "Pick only one stock to explore"
main_menu['2'] = "Pick multiple stocks (up to 5) to compare"
main_menu['Q'] = "Exit"

# main menu for multiple stocks comparison
mutli_ticker_menu = {}
mutli_ticker_menu['1'] = "Compare price movement"
mutli_ticker_menu['2'] = "Compare news sentiment"
mutli_ticker_menu['3'] = "Compare twitter sentiment over past 8 days"
mutli_ticker_menu['H'] = "Back to the main menu"
mutli_ticker_menu['Q'] = "Exit"

# main menu for a single stock exploration
a_ticker_menu = {}
a_ticker_menu['1'] = "Company overview" 
a_ticker_menu['2'] = "Stock price movement"
a_ticker_menu['3'] = "News analysis"
a_ticker_menu['4'] = "Twitter analysis over past 8 days"
a_ticker_menu['H'] = "Back to the main menu"
a_ticker_menu['Q'] = "Exit"

# "price" sub menu for a single stock exploration
a_ticker_price_menu = {}
a_ticker_price_menu['1'] = "Plot closing price and trading volume"
a_ticker_price_menu['2'] = "Plot closing price simple moving average"
a_ticker_price_menu['3'] = "Add more tickers to compare price"
a_ticker_price_menu['H'] = "Back to the main menu"
a_ticker_price_menu['M'] = "Back to the one stock exploration menu"
a_ticker_price_menu['Q'] = "Exit"


# "news" sub menu for a single stock exploration
a_ticker_news_menu = {}
a_ticker_news_menu['1'] = "Display the most recent 10 news headlines" 
a_ticker_news_menu['2'] = "Plot closing price vs news sentiment" 
a_ticker_news_menu['3'] = "Display new sentiment model summary on closing price"
a_ticker_news_menu['4'] = "News word cloud"
a_ticker_news_menu['5'] = "Add more tickers to compare news sentiment"
a_ticker_news_menu['H'] = "Back to the main menu"
a_ticker_news_menu['M'] = "Back to the one stock exploration menu"
a_ticker_news_menu['Q'] = "Exit"

# "twitter" sub menu for a single stock exploration
a_ticker_twitter_menu = {}
a_ticker_twitter_menu['1'] = "Plot twitter sentiment over past 8 days" 
a_ticker_twitter_menu['2'] = "Plot closing price vs twitter sentiment over past 8 days" 
a_ticker_twitter_menu['3'] = "Twitter sentiment model summary on price over past 8 days"
a_ticker_twitter_menu['4'] = "Tweet word cloud"
a_ticker_twitter_menu['5'] = "Add more tickers to compare twitter sentiment"
a_ticker_twitter_menu['H'] = "Back to the main menu"
a_ticker_twitter_menu['M'] = "Back to the one stock exploration menu"
a_ticker_twitter_menu['Q'] = "Exit"


# text printing styles for alert messages or user input message
invalid_style = colored.fg("red") + colored.attr("bold")
input_style = colored.fg("light_yellow") + colored.attr("bold")

def display_menu(menu_dict):
    '''
    Prints out a menu in a nice format
    
    Parameters
    ----------
    menu_dict(dict): a menu that is in a dictionary format
        
    '''
    options = list(menu_dict.keys())
    options.sort() #sort menu index
    
    print("\n    Please select one from the menu:")
    for entry in options: 
        print("    "+ entry + ")  " + menu_dict[entry])


def validate_choice(menu_dict, answer):
    '''
    Checks if a menu option entered by a user is one of the options provided
    by any menu.
    
    Parameters
    ----------
    menu_dict(dict): a menu that is in a dictionary format
    answer(string): a menu option entered by a user
    
    Returns
    -------
    True, if the menu option entered by a user is one of the options from the
    given menu.
    Otherwise, False.
    '''
    if answer.upper() in menu_dict.keys():
        return True
    else:
        return False


def validate_ticker(ticker):
    '''
    Checks if a stock ticker entered by a user is a valid.
    
    Parameters
    ----------
    ticker(string): a stock's ticker symbol entered by a user
    
    Returns
    -------
    True, if the ticker entered by a user is a valid ticker.
    Otherwise, False.
    '''
    
    # use function 'get_co_full_name' from sp module to check if the function 
    # can return its company's full name, given the ticker input.
    # if returning True, it means the ticker is valid, otherwise False.
    if sp.get_co_full_name(ticker.upper()) == False:
        return False
    else:
        return True
    

def valid_pagenum(pagenum_input):
    '''
    Checks if page number input (number of pages of news headlines a user wants
    to see about a stock) entered by the user is in a valid format.
    
    Parameters
    ----------
    pagenum_input(string): number of pages of news headlines a user wants to 
    see about a stock
        
    Returns
    -------
    True, if pagenum_input can be converted to an integer between 1 to 
    100.
    Otherwise, False.
    '''
    try:
        pagenum_input = int(pagenum_input)
        if 1 <= pagenum_input <= 100:
            return True
        else:
            return False
    except:
        return False
    
    
def check_start_date(date_text):
    '''
    Checks if a start date for a stock's price inquiry is entered properly by 
    a user.
    
    Parameters
    ----------
    date_text(string): a string that is supposed to be able to convert to a date
        
    Returns
    -------
    True, if date_text can be converted to a date with yyyy-mm-dd format AND 
    if date_text represents a date that is earlier than today.
    
    -1, if date_text represents a date that is earlier than today.
    
    False, if date_text cannot represent a date.
    '''
    date_today = datetime.today()
    
    try:
        actual_date = datetime.strptime(date_text, '%Y-%m-%d')
        
        if actual_date >= date_today - timedelta(days= 1):
            return -1
        else:
            return True
    
    except ValueError:
        return False


def check_end_date(date_text, start_date):
    '''
    Checks if an end date for a stock's price inquiry is entered properly by 
    a user, given a start date for the price inquiry.
    
    Parameters
    ----------
    start_date(string): a string that means the start date for a stock's 
    price inquiry

    Returns
    -------
    True, if date_text can be converted to a date with yyyy-mm-dd format AND 
    if date_text represents a date that is after the start date but no later
    than today.
    
    -1, if date_text represents a date that is earlier than start date.
    
    -2, if date_text represents a date that is after today.
    
    False, if date_text cannot represent a date.
    '''
    date_today = datetime.today()
    
    try:
        actual_date = datetime.strptime(date_text, '%Y-%m-%d')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        if actual_date <= start_date:
            return -1
        elif actual_date > date_today:
            return -2
        
        else:
            return True
    
    except ValueError:
        return False    

    
def ask_a_ticker():
    '''
    Gets a valid ticker from a user.
        
    Returns
    -------
    A string in uppercase, which means a valid ticker symbol.
    '''

    #ask user to enter a sticker
    ticker = input(stylize('    Please enter a ticker symbol:',
                           input_style)).strip().upper()
    #check if the ticker entered is valid
    cur_stauts = validate_ticker(ticker)
    
    # use while loop to keep asking the user until a valid ticker is entered
    while cur_stauts != True:
        print(stylize('\n    Invalid ticker symbol. Please enter again.', 
                      invalid_style))
            
        ticker = input(stylize('    Please enter a ticker symbol:', 
                               input_style)).strip().upper()
        
        cur_stauts = validate_ticker(ticker)
        
    return ticker.upper()


def ask_start_date():
    '''
    Gets a valid start date from users for a stock's price inquiry.
    
    Returns
    -------
    A string like 'yyyy-mm-dd' that can represent a date earlier than today.
    '''
    
    # ask a user to enter a start date for a stock's price inquiry
    price_start_date = input(stylize('    Start date (yyyy-mm-dd) for price inquiry:',
                                     input_style)).strip()
    
    # checks if the start date is valid
    cur_status = check_start_date(price_start_date)
    
    # use while loop to keep asking the user until a proper start date is entered
    while cur_status != True:
        # alert the user if the date entered is earlier than today
        if cur_status == -1:
            print (stylize('\n    Please enter a date that is earlier than today.',
                           invalid_style))
            
        # alert the user if the date entered is not valid
        else:
            print (stylize('\n    Invalid date format. Please enter again.', 
                           invalid_style))
            
        price_start_date = input(stylize('    Start date (yyyy-mm-dd) for price inquiry:',
                                         input_style)).strip()
        
        cur_status = check_start_date(price_start_date)
        
    return price_start_date


def ask_end_date(price_start_date):
    '''
    Gets a valid end date from users for a stock's price inquiry.
    
    Parameters
    ----------
    price_start_date(string):  a string that means the start date for a stock's 
    price inquiry
    
    Returns
    -------
    A string like 'yyyy-mm-dd' that can represent a date after the start date
    but no later than today.
    '''
    
    # ask a user to enter an end date for a stock's price inquiry
    price_end_date = input(stylize('    End date(yyyy-mm-dd) for price inquiry:',
                                   input_style)).strip()
    
    # check if the date entered is valid
    cur_status = check_end_date(price_end_date, price_start_date)
    
    # use while loop to keep asking the user until a valid end date is entered
    while cur_status != True:
        # alert the user if the date is after start date
        if cur_status == -1:
            print (stylize('\n    Please enter a date that is after start date.',
                           invalid_style))
        
        # alert the user if the date is after today
        elif cur_status == -2:
            print (stylize('\n    Please enter a date that is no later than today.',
                           invalid_style))
        
        # alert the user if the date entered is not valid
        else:
            print(stylize('\n    Invalid date format. Please enter again.',
                          invalid_style))
           
        price_end_date = input(stylize('    End date(yyyy-mm-dd) for price inquiry:',
                                       input_style)).strip()
        
        cur_status = check_end_date(price_end_date, price_start_date)
        
    return price_end_date


def ask_news_page():
    '''
    Gets a valid page number from a user for the number of pages of news 
    headlines he/she wants to extract.
    
    Returns
    -------
    A proper integer that represent the number of pages of news headlines 
    he/she wants to extract.
    '''
    
    # ask a user for number of pages of news headlines to extract
    pagenum = input(stylize('    Number of pages of news headlines to analyze (100 max):',input_style)).strip()
    
    # checks if the input entered by the user is valid
    cur_status = valid_pagenum(pagenum)
    
    # use while loop to keep asking the user until a proper page number is entered
    while cur_status == False:
        # alert the user if the input is invalid
        print(stylize('\n    Invalid page number entry. Please try again.',invalid_style))
        
        pagenum = input(stylize('    Number of pages of news headlines to analyze (100 max):',input_style)).strip()
        cur_status = valid_pagenum(pagenum)
        
    return int(pagenum)


def valid_ticker_count(ticker_count_input, max_count):
    '''
    Checks if the number of stock tickers a user entered is a valid integer
    that is less than or equal to a max number that is allowed.
    
    Parameters
    ----------
    ticker_count_input(string): a string that is supposed to be able to 
    convert to an integer that is <= max_count.
    
    max_count(integer): the max number of tickers a user can explore at one 
    time.
    
    Returns
    -------
    True, if ticker_count_input can be converted to an integer that is less 
    than or equal to max_count.
    
    Otherwise, False.
    '''
    try:
        ticker_count_input = int(ticker_count_input)
        if 1 <= ticker_count_input <= max_count:
            return True
        else:
            return False
    except:
        return False

    
def ask_4max_tickers(ticker):
    '''
    Gets a list of stock tickers a user wants to compare at one time, while 
    he/she is currently exploring one ticker.
    
    This function will be used when the user wants to compare the ticker with
    additonal tickers (at least 1 more ticker, and 4 at most).
    
    Parameters
    ----------
    ticker(string): a stock ticker the user is currently exploring.
    
    Returns
    -------
    A list that contains 2 to 5 ticker symbols (including the ticker the user
    is currently exploring).
    '''
    
    ticker_list = [ticker]
    
    # ask a use to enter the number of addtional tickers he/she wants to compare
    ticker_count = input(stylize("    Number of tickers you want to add (4 max):", input_style))
    
    # check if the ticker size enterd is valid
    cur_status = valid_ticker_count(ticker_count, 4) 
    
    # use while loop to keep asking the user until a valid ticker size is entered
    while cur_status == False:
        # alert the user if the input is not valid.
        print(stylize('\n    Invalid entry. Please try again.', invalid_style))
        ticker_count = input(stylize("    Number of tickers you want to add:", 
                                     input_style))
        
        cur_status = valid_ticker_count(ticker_count, 4) 
    
    # create the ticker list
    i = 1
    while i < int(ticker_count) +1:
        # get ticker input that the user wants to compare with the current one
        ticker = input("    Ticker " + str(i) +":").strip().upper()
        
        # alert the user if the ticker entered is already in the list
        if ticker in ticker_list:
            print(stylize("\n    Duplicate entry. Please enter a different ticker.", invalid_style))
        
        else:
            if sp.get_co_full_name(ticker) != False:
                ticker_list.append(ticker) #append to the list
                i +=1
                
            # alert the user if the ticker is invalid
            else:
                print(stylize("\n    Invalid ticker. Please try again.", invalid_style))
    
    return ticker_list

    
def ask_5max_tickers():
    '''
    Gets a list of stock tickers a user wants to compare at one time.
    
    This function will be used when the user wants to compare up to 5 tickers
    at a time.
    
    Returns
    -------
    A list that contains 2 to 5 ticker symbols.
    '''
    ticker_list = list()
    # ask a user to enter the number of tickers he/she wants to compare
    ticker_count = input(stylize("    Number of tickers you want to compare (5 max):",input_style))
    
    # checks if the ticker size is valid
    cur_status = valid_ticker_count(ticker_count, 5) 
    
    # use while loop to keep asking user until a valid ticker size is entered
    while cur_status == False:
        # alert the user if the input is invalid
        print(stylize('\n    Invalid entry. Please try again.', invalid_style))
        ticker_count = input(stylize("    Number of tickers you want to compare (5 max):",
                                     input_style))
        cur_status = valid_ticker_count(ticker_count, 5) 
        
    # create the ticker list
    i = 1
    while i < int(ticker_count) +1:
        # gets ticker symbol one by one
        ticker = input("    Ticker " + str(i) +":").strip().upper()
        
        # alert the user if the ticker entered is already in the list
        if ticker in ticker_list:
            print(stylize("\n    Duplicate entry. Please enter a different ticker.", 
                          invalid_style))
        
        else:
            #append to the ticker list if it is a valid ticker
            if sp.get_co_full_name(ticker) != False:
                ticker_list.append(ticker)
                i +=1
                
            # alert the user if the ticker is not a valid input
            else:
                print(stylize("\n    Invalid ticker. Please try again.", 
                              invalid_style))
    
    return ticker_list


def display_main_menu():
    '''
    Prints out the main menu in a nice format, while asking a user for menu 
    option input.
    
    This function will be used when a user just starts the program or when 
    he/she selects to go back to see the main menu.
    
    Returns
    -------
    Different menus depends on the user's choice
    '''
    cur_status = True
    menu = main_menu
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        # display the main menu
        display_menu(menu) 
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', invalid_style))
            
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
            
        # display the main menu for a single stock exploration
        elif ans == '1':
            return display_a_ticker_menu()
        
        # displays the main menu for multiple stocks comparison
        elif ans == '2':
            return display_5max_ticker_menu()
        
        
def display_5max_ticker_menu():
    '''
    Prints out the main menu for multiple stocks comparison in a nice format, 
    while asking a user for menu option input.
    
    This function will be used when a user chooses to compare multiple tickers
    at a time.
    
    Returns
    -------
    The main menu if the user chooses so.
    '''
    cur_status = True
    menu = mutli_ticker_menu
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        # display the main menu for multiple stocks comparison
        display_menu(menu)
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', 
                          invalid_style))
         
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
         
        # display the main menu
        elif ans.lower() == 'h':
            return display_main_menu()
            
        else:
            # get a ticker list from the user that contains 5 tickers at most, 
            # if the user chooses an option that is not Q or H
            ticker_list = ask_5max_tickers()
        
            # gets the start and end date for price inquiry from the user,
            # then displays a plot for price movement comparion for all tickers
            # between the start date and the end date
            if ans == '1':
                price_start_date = ask_start_date()
                price_end_date = ask_end_date(price_start_date)
                sp.plot_multi_price(ticker_list, price_start_date, price_end_date)
            
            # gets the number of pages of news headlines the user wants to extract
            # then displays a plot for news sentiment movement comparison for 
            # all tickers
            elif ans == '2':
                pagenum = ask_news_page()
                sn.plot_mutli_news_sa(ticker_list, pagenum)
             
            # displays a plot for tweet sentiment movement comparison for 
            # all tickers over the past 8 days
            elif ans == '3':
                st.plot_multi_tweet_sa(ticker_list)
                
        
def display_a_ticker_menu():
    '''
    Prints out the main menu for a single stock exploration in a nice format, 
    while asking a user for menu option input.
    
    This function will be used when a user chooses to explore only one stock
    ticker at a time.
    
    Returns
    -------
    Different menus depends on the user's choice
    '''
    
    cur_status = True
    menu = a_ticker_menu
    ticker = ""
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        #display the main menu for a single stock exploration
        display_menu(menu)
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', 
                          invalid_style))
         
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
        
        # display the main menu
        elif ans.lower() == 'h':
            return display_main_menu()
            
        else:
            # ask for a valid ticker if the user chooses an option other than
            # H or Q.
            while ticker == "":
                ticker = ask_a_ticker()
            
            # display the stock company's profile
            if ans == '1':
                sf.display_profile(ticker)
            
            # gets the start and end date for price inquiry from the user
            # then displays "price" sub menu for a single stock exploration
            elif ans == '2':
                price_start_date = ask_start_date()
                price_end_date = ask_end_date(price_start_date)
    
                return display_a_ticker_price_menu(ticker, 
                                                   price_start_date, 
                                                   price_end_date)
            # gets the number of pages of news headlines the user wants to extract
            # then displays "news" sub menu for a single stock exploration
            elif ans == '3':
                pagenum = ask_news_page()
                return display_a_ticker_news_menu(ticker, pagenum)
            
            # displays "twitter" sub menu for a single stock exploration
            elif ans == '4':
                return display_a_ticker_twitter_menu(ticker)
            
        
def display_a_ticker_price_menu(ticker, price_start_date, price_end_date):  
    '''
    Prints out the "price" sub menu for a single stock exploration in a 
    nice format, while asking a user for menu option input.
    
    This function will be used when a user chooses to explore one stock
    ticker's price movement.
    
    Parameters
    ----------
    price_start_date(string): a string that means the start date for a stock's 
    price inquiry
    
    price_end_date(string): a string that means the end date for a stock's 
    price inquiry
    
    Returns
    -------
    Different menus depends on the user's choice
    '''
    
    menu = a_ticker_price_menu
    cur_status = True
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        #display the "price" sub menu for a single stock exploration
        display_menu(menu)
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', invalid_style))
            
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
        
        # display the main menu   
        elif ans.lower() == 'h':
            return display_main_menu()
        
        # display the main menu for a single stock exploration
        elif ans.lower() == 'm':
            return display_a_ticker_menu()
        
        # display a plot for the ticker's price and trading volume movement
        # between the start and end date
        elif ans.lower() == '1':
            sp.plot_price_volm(ticker, price_start_date, price_end_date)
            print('\n')
        
        # display a plot of the ticker's price simple moving average between
        # the start and end date
        elif ans.lower() == '2':
            sp.plot_sma(ticker, price_start_date, price_end_date)
            print('\n')
        
        # gets a list of tickers the user wants to compare with the current one
        # then asks for the start and end date of stock price inquiry
        # then displays a plot of price movement comparison for all tickers 
        # between the start and end date
        elif ans.lower() == '3':  
            ticker_list = ask_4max_tickers(ticker)
            price_start_date = ask_start_date()
            price_end_date = ask_end_date(price_start_date)
            
            sp.plot_multi_price(ticker_list,price_start_date, price_end_date)
            print('\n')

            
def display_a_ticker_news_menu(ticker, pagenum):    
    '''
    Prints out the "news" sub menu for a single stock exploration in a nice 
    format, while asking a user for menu option input.
    
    This function will be used when a user chooses to explore one stock
    ticker's news sentiment movement.
    
    Parameters
    ----------
    ticker(string):  a stock ticker
    pagenum(int): number of pages of news headlines the user wants to extract
    
    Returns
    -------
    Different menus depends on the user's choice
    '''
    menu = a_ticker_news_menu
    cur_status = True
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        # displays the "news" sub menu for a single stock exploration
        display_menu(menu)
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', 
                          invalid_style))
            
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
        
        # display the main menu   
        elif ans.lower() == 'h':
            return display_main_menu()
        
        # display the main menu for a single stock exploration
        elif ans.lower() == 'm':
            return display_a_ticker_menu()
           
        # display top 10 news headlines for the ticker
        elif ans.lower() == '1':
            sn.display_news_10(ticker, pagenum)
        
        # ask for the start date of stock price inquiry if the users selects 
        # 2 or 3
        elif ans.lower() == '2' or ans.lower() == '3':
            price_start_date = ask_start_date()
            print('\n')
            
            # display a plot of price vs news sentiment movement for the stock, 
            # where the duration will be an overlapped period of the price inquiry 
            # date range and the news data date range
            if ans.lower() == '2':
                sn.plot_news_sa_price(ticker, price_start_date, pagenum)
                print('\n')
            
            # display a statistical model summary of news sentiments' significance
            # on the stock's closing price
            # then displays a plot of the stock's actual closing price vs model
            # price.
            # date range of the plot is an overlapped period of the price inquiry 
            # date range and the news data date range
            elif ans.lower() == '3':
                sn.model_news_sa_price(ticker, price_start_date, pagenum)
                print('\n')
        
        # display the stock's word cloud based on news
        elif ans.lower() == '4':
            wc.create_news_worldcloud(ticker, pagenum)
            print('\n')
            
        # gets a list of tickers the user wants to compare with the current one
        # then displays a plot of the news sentiment comparison
        elif ans.lower() == '5':
            ticker_list = ask_4max_tickers(ticker)
            sn.plot_mutli_news_sa(ticker_list, pagenum)
            print('\n')

        
def display_a_ticker_twitter_menu(ticker):  
    '''
    Prints out the "twitter" sub menu for a single stock exploration in a nice 
    format, while asking a user for menu option input.
    
    This function will be used when a user chooses to explore one stock
    ticker's twitter sentiment movement over the past 8 days.
    
    Parameters
    ----------
    ticker(string):  a stock ticker
    
    Returns
    -------
    Different menus depends on the user's choice
    '''
    
    menu = a_ticker_twitter_menu
    cur_status = True
    
    # while loop to ask a user for a valid menu selection
    while cur_status == True:
        # displays the "twitter" sub menu for a single stock exploration
        display_menu(menu)
        
        # ask a user for a menu option
        ans = input(stylize("    Your choice:", input_style)).strip()
        
        # alert the user if the input is not a valud menu selection
        if validate_choice(menu, ans) == False:
            print(stylize('\n    Invalid choice. Please enter again.', invalid_style))
         
        # quit the program if the user selects to exit
        elif ans.lower() == 'q':
            cur_status = False
            print('\n************ Thanks for using ' + myCompanyName + '! ******')
        
        # display the main menu       
        elif ans.lower() == 'h':
            return display_main_menu()
        
        # display the main menu for a single stock exploration
        elif ans.lower() == 'm':
            return display_a_ticker_menu()
        
        # displays the ticker's tweets sentiment movement over the past 8 days
        elif ans.lower() == '1':
            st.plot_twitter_sa(ticker)
            print('\n')
        
        # displays the ticker's tweets sentiment movement vs price movement
        # over the past 5 business dys.
        elif ans.lower() == '2':
            st.plot_twitter_sa_price(ticker)
            print('\n')
        
        # display a statistical model summary of tweet sentiments' significance
        # on the stock's closing price
        # then displays a plot of the stock's actual closing price vs model
        # price.
        # date range is the past 5 business dys.
        elif ans.lower() == '3':  
            st.model_tweet_sa_price(ticker)
            print('\n')
            
        # display the stock's word cloud based on tweets
        elif ans.lower() == '4':
            wc.create_tweet_worldcloud(ticker)
            
        # gets a list of tickers the user wants to compare with the current one
        # then displays a plot of the tweets sentiment comparison over the past
        # 8 days
        elif ans.lower() == '5':
            ticker_list = ask_4max_tickers(ticker)
            st.plot_multi_tweet_sa(ticker_list)
            print('\n')
            
            
# run the following if the current module is the main module
if __name__ == "__main__":
    print('************ Welcome to ' + myCompanyName + '! ************' )
    display_main_menu()
        
        
        
        
            
      
            
        
            
            
            
            
            
            
            
            
        

        
