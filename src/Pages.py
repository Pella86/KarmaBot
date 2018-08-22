# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 23:26:12 2018

@author: Mauro
"""
#==============================================================================
# Imports
#==============================================================================
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

import BotWrappers
import NumberFormatter

#==============================================================================
# helpers
#==============================================================================
def Button(text, cb):    
    return InlineKeyboardButton(text=text, callback_data=cb)

#==============================================================================
# Pages base class
#==============================================================================
class Pages:
    
    def __init__(self, title, page, max_per_page, query_tag, query = None):
        self.title = title
        self.page = page
        self.max_per_page = max_per_page
        self.query_tag = query_tag
        self.query = query

    def get_page_list_indexes(self):
        start = self.page * self.max_per_page
        end = start + self.max_per_page
        return (start, end)     
    
    def calcTotPages(self, org_list):
        return int(len(org_list) / self.max_per_page)
    
    def sendPage(self, bot, user, list_of_elements,  tot_pages):
        s = "<b>" + self.title + "</b>\n"
        s += "\n"
        
        for i in range(0, self.max_per_page):
            if i >= len(list_of_elements):
                break
            else:
                s += list_of_elements[i] + "\n"
                s += "\n"
        s += "\n"     
        
        s += "/main_menu      {}/{}".format(self.page + 1, tot_pages + 1)
        
        text = "<"
        callback_data = self.query_tag  + str(self.page)  + "_" + "prev"
        b_prev = BotWrappers.Button(text, callback_data)

        text = ">"
        callback_data = self.query_tag  + str(self.page) + "_" + "succ"
        b_succ = BotWrappers.Button(text, callback_data)
        
        keyboard = BotWrappers.ReplyKeyboard()
        keyboard.addButtonLine([b_prev, b_succ])

        rmk = keyboard.getKeyboard()

        if self.query is not None:
            BotWrappers.editMessage(bot, user, self.query.getChatMsgID(), s, translation = False, reply_markup=rmk, parse_mode="HTML")
        else:
            BotWrappers.sendMessage(bot, user, s, translation=False, reply_markup=rmk, parse_mode="HTML")     

#==============================================================================
# TopTenUserList
#==============================================================================

class TopTenUserListPages(Pages):
    def __init__(self, page, user, usersdb, query=None):
        super().__init__("-- Top Ten --", page, 10, "cp_usertt_", query)   
        self.users_list = usersdb.getUsersList()
        self.users_list.sort(key=lambda x : x.getReputation(), reverse=True)
    
    def create_element_list(self):
        elements = []
        for i in range(*self.get_page_list_indexes()):
            if i < len(self.users_list):
                user = self.users_list[i]

                s = "<code>{index}. {username:_^15} --- {reputation}</code>"
                
                sdb = {}
                sdb["index"] = str(i + 1)
                sdb["username"] = user.display_id
                sdb["reputation"] = user.getReputationF()
                
                s = s.format(**sdb)
                
                elements.append(s)
        return elements

    def check_answer(self, bot, user, prev):
        if prev:
            self.page -= 1
            if self.page < 0:
                bot.answerCallbackQuery(self.query.id, "Reached first page")
                return
        else:
            self.page += 1
            if self.page > self.calcTotPages(self.users_list):
               bot.answerCallbackQuery(self.query.id, "Reached last page")
               return
        
        self.sendPage(bot, user) 
    
    def sendPage(self, bot, user):
        super().sendPage(bot, user, self.create_element_list(), self.calcTotPages(self.users_list))
                
#
##==============================================================================
## Uploaded Media Pages
##==============================================================================
#
#class UploadedMediaPages(Pages):
#
#    def __init__(self, page, user, mediavotedb, query=None):
#        super().__init__("Uploaded media", page, 10, "cp_umedia_", query) 
#
#        self.medialist = mediavotedb.getUserMedia(user) 
#    
#    def create_element_list(self):
#        elements = []
#        for i in range(*self.get_page_list_indexes()):
#            if i < len(self.medialist):
#                media = self.medialist[i]
#                
#                sdb = {}
#                sdb["n"] = str(i)
#                sdb["media_type"] = media.content.type
#                sdb["cat_name"] = media.cat_name #this would not be capitalized
#                sdb["up"] = NumberFormatter.UpVotes(media.upvotes)
#                sdb["down"] = NumberFormatter.DownVotes(media.downvotes)
#                sdb["uid"] = str(media.uid)
#                sdb["score"] = NumberFormatter.FormatNumber(media.calculateScore(), 0)
#                
#                s = "{n}. {media_type} | {cat_name}\n"
#                s += "{up} - {down} | {score}\n"
#                s += "/show_{cat_name}_{uid}"
#                
#                s = s.format(**sdb)
#                
#                elements.append(s)
#        return elements
#    
#    def sendPage(self, bot, user):
#        super().sendPage(bot, user, self.create_element_list(), self.calcTotPages(self.medialist))
#
#   
##==============================================================================
## User top pages
##==============================================================================
#class UserTopPages(Pages):
#    
#    def __init__(self, page, user_list, query=None):
#        super().__init__("Users top", page, 10, "cp_utop_", query)
#        
#        self.ulist = user_list
#    
#    def create_element_list(self):
#        elements = []
#        for i in range(*self.get_page_list_indexes()):
#            if i < len(self.ulist):
#                user = self.ulist[i]
#                
#                sdb = {}
#                sdb["pos"] = str(i)
#                sdb["name"] = user.display_id
#                sdb["rep"] = NumberFormatter.Reputation(user.getReputation())
#                elem = "<code>{pos}.{name:_^15}|{rep}</code>".format(**sdb)
#                elements.append(elem)
#            else:
#                break
#        return elements
#    
#    def check_answer(self, bot, user, prev):
#        if prev:
#            self.page -= 1
#            if self.page < 0:
#                bot.answerCallbackQuery(self.query.id, "Reached first page")
#                return
#        else:
#            self.page += 1
#            if self.page > self.calcTotPages(self.ulist):
#               bot.answerCallbackQuery(self.query.id, "Reached last page")
#               return
#        
#        self.sendPage(bot, user)
#        
#    def sendPage(self, bot, user):
#        super().sendPage(bot, user, self.create_element_list(), self.calcTotPages(self.ulist))
#                
##==============================================================================
## Categories base class
##==============================================================================
#
#class CategeroyPagesBase(Pages):
#    
#    def __init__(self, page, max_per_page, cat_list, query_tag, query):
#        super().__init__("Categories", page, max_per_page, query_tag, query)
#        
#        self.cat_list = cat_list
#    
#    def base_create_element_list(self, *argc, **kwargs):
#        elements = []
#        
#        for i in range(*self.get_page_list_indexes()):
#            if i < len(self.cat_list):
#                s = self.create_element(self.cat_list, i, *argc, **kwargs)
#                elements.append(s)
#            else:
#                break
#        return elements    
#    
#
#    def base_check_answer(self, bot, user, prev, *args, **kwargs):
#        if prev:
#            self.page -= 1
#            if self.page < 0:
#                bot.answerCallbackQuery(self.query.id, "Reached first page")
#                return
#        else:
#            self.page += 1
#            if self.page > self.calcTotPages(self.cat_list):
#                bot.answerCallbackQuery(self.query.id, "Reached last page")
#                return
#
#        self.sendPage(bot, user,  *args, **kwargs)  
#
##==============================================================================
## Categories
##==============================================================================
#class CategoryPages(CategeroyPagesBase):
#    
#    def __init__(self, page, cat_list, query=None):
#        super().__init__(page, 3, cat_list, "cp_cat_", query)
#
#    def create_element(self, cat_list, i, user, mediavotedb):
#        s = "~~~~ " + cat_list[i].display_name + " ~~~~" + "\n"
#        n_voted, total = user.countVoted(cat_list[i].name_id, mediavotedb)
#        if total == 0:
#            s += "Empty\n"
#        else:
#            s += "Voted: {} / {}\n".format(n_voted, total)
#        
#        s += "Category score: " + str(NumberFormatter.FormatNumber(cat_list[i].score, 0)) + "\n"
#        
#        if n_voted == total:
#            s += "/show_" + cat_list[i].display_name
#        else:
#            s += "/vote_" + cat_list[i].display_name
#            
#        #user_voted_all = get media if user in  already voted
#        #calc tot for media in media list if not hide nor ban
#        # if voted == tot -> show
#        # else -> vote
#        
#        return s  
#    
#    def create_element_list(self, user, mediavotedb):
#        return self.base_create_element_list(user, mediavotedb)
#
#    def check_answer(self, bot, user, prev, mediavotedb):
#        self.base_check_answer(bot, user, prev, mediavotedb)        
#
#    def sendPage(self, bot, user, mediavotedb):
#        list_of_elements = self.create_element_list(user, mediavotedb)
#        tot_pages = self.calcTotPages(self.cat_list)
#        super().sendPage(bot, user, list_of_elements, tot_pages)
#
##==============================================================================
## Categories condensed
##==============================================================================
#
#class CategoryPagesShort(CategeroyPagesBase):
#    
#    def __init__(self, page, cat_list, query=None):
#        super().__init__(page, 6, cat_list, "cp_shortcat_", query)
#        
#    def create_element(self, cat_list, i):
#        s = "<b>-- " + cat_list[i].display_name + " --</b>" + "\n"
#        s += "Score: " + str(NumberFormatter.FormatNumber(cat_list[i].score, 0))
#        return s  
#
#    def check_answer(self, bot, user, prev):
#        self.base_check_answer(bot, user, prev) 
#    
#    def sendPage(self, bot, user):
#        list_of_elements = self.base_create_element_list()
#        tot_pages = self.calcTotPages(self.cat_list)
#        super().sendPage(bot, user, list_of_elements, tot_pages)
#    
##==============================================================================
## Categories List   
##==============================================================================
#
#class CategoryList(CategeroyPagesBase):
#
#    def __init__(self, page, cat_list, query=None):
#        super().__init__(page, 10, cat_list, "cp_catlist_", query)
#    
#    def create_element(self, cat_list, i):
#        s = "{}".format(cat_list[i].display_name) + "\n"
#        s += "/catinfo_{}".format(cat_list[i].name_id)
#        return s
#
#    def check_answer(self, bot, user, prev):
#        self.base_check_answer(bot, user, prev) 
#    
#    def sendPage(self, bot, user):
#        list_of_elements = self.base_create_element_list()
#        tot_pages = self.calcTotPages(self.cat_list)
#        super().sendPage(bot, user, list_of_elements, tot_pages)
#      
