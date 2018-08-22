# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 12:11:02 2018

@author: Mauro
"""

# KarmaBot
# A bot to keep track of karma and likes
# have a info panel
# have a help panel
# highest rated message per user
# silent mode
# buy reputation
# multiple groups


__version__ = "0.0.1"


# import sys to access the src folder
import sys
sys.path.append("./src")


#==============================================================================
# Imports
#==============================================================================

#py imports
import time
import string

# telepot imports
import telepot
from telepot.loop import MessageLoop

# my imports
import BotDataReader
import Logging
import MessageParser
import PersonDB
import UsersDB
import NumberFormatter
import BotWrappers
import Pages
import EmojiTable

#==============================================================================
# Logging
#==============================================================================

# create logger
log = Logging.get_logger(__name__, "DEBUG")

def LogBigMistakes(func):
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            log.exception(func.__name__ + ": Big mistake")
    return func_wrapper

#==============================================================================
# Rate class
#==============================================================================

class Rate:
    '''
    Rate

    small class to manage fps and various update rates
    '''

    def __init__(self, rate):
        '''Initialize the rate calling for the time function

        Keyword argument:
        rate -- is a float representing 1/s frame rate
        '''

        self.rate = rate
        self.init_time = True

    def is_time(self):
        ''' Returns true if the current time surpasses the rate
            and resets the timer
        '''
        
        # start the first time
        if self.init_time == True:
            self.init_time = time.time()
            log.debug("is time first time")
            return True            

        # wait for the rate to happen
        if time.time() - self.init_time > self.rate:
            self.init_time = time.time()
            log.debug("is time")
            return True
        else:
            return False

#==============================================================================
# constants    
#==============================================================================


waiting_signal = ['-', '/', '|', '\\']
waiting_counter = 0

# voting symbols
positive_voting_ascii = ['+', '+1']
positive_voting_emojii = ['\U0001F44D'.encode("UTF-8")]

negative_voting_ascii = ['-', '-1']  
negative_voting_emojii = ['\U0001F44E'.encode("UTF-8")]

pv_commands = ["/set_nickname"]


show_top_rate = Rate(60*20) # 20 minutes

#==============================================================================
# helper functions
#==============================================================================

def check_positive(text):
    if text in positive_voting_ascii:
        return True
    
    elif text.encode("UTF-8") in positive_voting_emojii:
        return True
    
    else:
        return False

def check_negative(text):
    if text in negative_voting_ascii:
        return True
    
    elif text.encode("UTF-8") in negative_voting_emojii:
        return True
    
    else:
        return False
    
def is_voting_symbol(text):
    if check_positive(text):
        return True
    elif check_negative(text):
        return True
    else:
        return False




#==============================================================================
# Handle
#==============================================================================


def handle_points(giving_user, msg):
    log.debug("giving/receiving karma")
    # add receiving user to db
    usersdb.addUser(msg.reply.mfrom, msg.reply.mfrom.id)
    receiving_user = usersdb.getUser(msg.reply.mfrom)         
        
    # send a message if is the first time 
    if giving_user.first_giving_karma:
        bot.sendMessage(msg.chat.id, "You gave/taken karma from somebody, you received {}, check your status at {}.".format(NumberFormatter.PellaCoins(1), bot_data.tag), reply_to_message_id=msg.message_id)
        giving_user.first_giving_karma = False

    
    if check_positive(msg.content.text):
        # add both users, sending karma, receiving if is not in the database
        giving_user.pella_coins += 1

        if receiving_user.karma is None:
            receiving_user.karma = 0
        receiving_user.karma += 1
        
        message = "+{} karma ({}) , from {}.".format(NumberFormatter.Karma(1), receiving_user.getReputationF(), giving_user.display_id) 
        bot.sendMessage(msg.chat.id, message, reply_to_message_id=msg.reply.message_id)
    
    elif check_negative(msg.content.text):
        # add both users, sending karma, receiving if is not in the database
        giving_user.pella_coins += 1

        if receiving_user.karma is None:
            receiving_user.karma = 0
        receiving_user.karma -= 1
        
        message = "-{} karma ({}), from {}.".format(NumberFormatter.Karma(1),receiving_user.getReputationF(), giving_user.display_id) 
        bot.sendMessage(msg.chat.id, message, reply_to_message_id=msg.reply.message_id)
        
        usersdb.setUser(receiving_user)
        
    usersdb.setUser(giving_user)
    usersdb.update()    

def handle_text_message(msg):
    if msg.mfrom.id != msg.reply.mfrom.id:
        if is_voting_symbol(msg.content.text):      
            
            # add giving user to db
            usersdb.addUser(msg.mfrom, msg.mfrom.id)
            giving_user = usersdb.getUser(msg.mfrom) 
            
            if giving_user.canGiveKarma():
                handle_points(giving_user, msg)
                giving_user.addKarmaGiven()                
            
            else:
                BotWrappers.sendMessage(bot, giving_user, "You gave enough karma, it realoads once a day.")


def handle_supergroup(msg):
    global show_top_rate
    if msg.content_type == "text" and msg.reply is not None:
        handle_text_message(msg)
    elif msg.content_type == "text" and ((msg.content.text == "/show_top" or msg.content.text == "/show_top" + bot_data.tag) and show_top_rate.is_time()):
        # get user list then sort for reputation 
        # display the first 10 names
        # keep a timer 
        userlist = usersdb.getUsersList()
        
        userlist.sort(key= lambda x : x.getReputation(), reverse=True)
        
        s = EmojiTable.trophy + " <b>-- Top Ten --</b> " + EmojiTable.trophy +"\n"
        for i, name in enumerate(userlist[:10]):
            s += "<code>{:0>2}.{:_^15}: {}</code>\n".format(i + 1, name.display_id, name.getReputationF())
            
        
        bot.sendMessage(msg.chat.id, s, parse_mode="HTML")

def handle_nickname_change(msg, user):
    
    if msg.content.type == "text":
        if msg.content.text != "/cancel":
            # rules for nickname
            # nickname should be shorter than 15 and above 3 characters
            # allowed @ + ascii
            username = msg.content.text
            if UsersDB.check_nickname(username):
                user.display_id = username
                BotWrappers.sendMessage(bot, user, "Nickname changed successfully\n/main_menu")
            else:
                #invalid character
                BotWrappers.sendMessage(bot, user, "Invalid character in nickname")
                user.sendUserProfile(bot)
        else:
            BotWrappers.sendMessage(bot, user, "Cancelled")
            # cancel
            # send profile
            user.sendUserProfile(bot)
    else:
        #invalid nickname
        # send profile
        BotWrappers.sendMessage(bot, user, "Invalid nickname must be text")
        user.sendUserProfile(bot)
    user.tmp_display_id = None
    return user
    
def handle_private(msg):
    
    # add user
    usersdb.addUser(msg.mfrom, msg.mfrom.id)
    user = usersdb.getUser(msg.mfrom)        
    
    # show the welcome messsage
    if user.first_private:
        welcome_message = "<b>Karma Bot</b>\nWelcome to your profile, here you can check your points and the best voted messages."
        BotWrappers.sendMessage(bot, user, welcome_message, parse_mode="HTML")
        user.first_private = False
    
    
    if user.tmp_display_id is True:
        user = handle_nickname_change(msg, user)
    
    if msg.content.type == "text":
        
        if msg.content.text == "/set_nickname":
            # ask the user to provide a nickname
            # set user.
            BotWrappers.sendMessage(bot, user, "Send a nickname. Allowed characters [a-z, A-Z, @]")
            user.tmp_display_id = True
        elif msg.content.text == "/main_menu":
            user.sendUserProfile(bot)
        elif msg.content.text == "/user_top":
            p = Pages.TopTenUserListPages(0, user, usersdb)
            p.sendPage(bot, user)
        else:
            user.sendUserProfile(bot) 
    else:
        # show the profile
        user.sendUserProfile(bot) 
    return user

@LogBigMistakes
def handle(raw_msg):
    global waiting_counter
    print("processing message " + waiting_signal[waiting_counter % len(waiting_signal)], end="\r")
    waiting_counter += 1

    msg = MessageParser.Message(raw_msg)
    
    persondb.addPerson(msg.mfrom)
    
    # if the person sends a voting symbol
    
    # select text messages and replies
    if msg.chat.type == "supergroup":
        handle_supergroup(msg)
    
    
    if msg.chat.type == "private":
        user = handle_private(msg)
        
        usersdb.setUser(user)
        usersdb.update()

    persondb.update()
    
@LogBigMistakes
def query(raw_msg):
    query = MessageParser.CbkQuery(raw_msg, False)
    
    query.initOptionals()
    
    # warning user might not be in the database
    user = usersdb.getUser(query.person)
    
    if query.data.startswith("cp_"):
        cmd_list = query.data.split("_")
        
        if len(cmd_list) < 4:
            raise Exception("list too short")

        page_n = int(cmd_list[2])
        prev = True if cmd_list[3] == "prev" else False        

        if cmd_list[1] == "usertt":
            p = Pages.TopTenUserListPages(page_n, user, usersdb, query)
            
            p.check_answer(bot, user, prev)
               
#==============================================================================
# Main
#==============================================================================

if __name__ == "__main__":
    log.info("\n--- Karma bot---")
    
    bot_data = BotDataReader.BotDataReader("./botdata/bot_data.tbot")
    #bot_data.prepareServerRouting()    
    
    bot = telepot.Bot(bot_data.token)
    
    bot_data.updateDataFile(bot)
    
    log.info("Bot data read, bot ready")
    
    persondb = PersonDB.PersonDB()
    usersdb = UsersDB.UsersDB()
    
    log.info("Databases loaded")
    
    
    #usersdb.database.updateDatabaseEntry({"tmp_display_id": lambda x : None})
    
    log.info("Databases updated")
    
    
    try:
        response = {
                'chat': handle,
                'callback_query': query
                #,
                #'inline_query': inline_query,
                #'chosen_inline_result' : chosen_inline
                }
    
        MessageLoop(bot, response).run_as_thread()
    except Exception as e:
        log.exception("main: Big mistake")
    
    log.info("Message loop started")
    
    while 1:
        time.sleep(10)    



