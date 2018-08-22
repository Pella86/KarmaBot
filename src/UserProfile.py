# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 18:28:37 2018

@author: Mauro
"""

#==============================================================================
# Imports
#==============================================================================
import datetime

import NumberFormatter
import BotWrappers

#==============================================================================
# User class
#==============================================================================
class UserProfile:
    
    
    def __init__(self, hash_id, display_id, chatid, lang_tag):
        # ids and stuff
        self.hash_id = hash_id
        self.display_id = display_id 
        self.chatid = chatid
        
        # points and karma
        self.pella_coins = 0
        self.karma = None
        self.rep_points = 1
        
        # tmp nickname
        self.tmp_display_id = None
        
        # first time
        self.first_giving_karma = True
        self.first_private = True
        
        # karma given count
        self.karma_given = 0
        self.karma_time = datetime.datetime.now()
        
        # various flags
        self.banned = False
        self.isActive = True
        
        # notifications
        #   notification tag : true, false
        self.notifications = {}
        
        # language tag
        self.lang_tag = lang_tag
        
        # join date
        self.join_date = datetime.datetime.now()
    
    def getReputationF(self):
        return NumberFormatter.Reputation(self.getReputation())
    
    def addKarmaGiven(self):
        if self.karma_given == 0:
            self.karma_time = datetime.datetime.now()
        
        self.karma_given += 1
    
    def canGiveKarma(self):
        if self.karma_given < 5:
            return True
        dtime = datetime.datetime.now() - self.karma_time
        if dtime.total_seconds() > (60*60*24):
            self.karma_given = 0
            self.karma_time = datetime.datetime.now()
            return True
        return False
        
    def getReputation(self):
        karma = self.karma if self.karma else 0
        karma = karma if karma > 0 else 0
        
        tdelta = datetime.datetime.now() - self.join_date
        days = tdelta.total_seconds() / (60*60*24)
        
        days = 1 if days < 1 else days
        
        return (karma * self.rep_points) / days**2
        

    def sendUserProfile(self, bot):
        # add a rmk to buy rep_points
        
        s = "<b>User Profile </b>\n"
        s += "<i>Your anonymous id is: {anon_id}</i>\n"
        s += "<i>Change nickname</i> "
        s += "/set_nickname" + "\n"
        s += "\n"
        s += "Coins: {pella_coins}\n"
        s += "Karma: {karma}\n"
        s += "Shield points: {rep_points}\n"
        s += "Repuation: {reputation}\n"
        s += "\n"
        s += "<b>--- User Top ---</b>\n"
        s += "<i> The bot top chart </i>\n"
        s += "/user_top\n"
        s += "\n"
        s += "<b>--- Karma count ---</b>\n"
        s += "<i> How much karma you distributed today </i>\n"
        s += "Karma given: {karma_given}\n"
        s += "Hours since last karma: {karma_given_hours}/24"
        s += "\n"    
        
        sdb = {}
        sdb["anon_id"] = self.display_id
        sdb["pella_coins"] = NumberFormatter.PellaCoins(self.pella_coins)
        sdb["karma"] = NumberFormatter.Karma(self.karma if self.karma else 0)        
        sdb["rep_points"] = NumberFormatter.RepPoints(self.rep_points)
        sdb["reputation"] = NumberFormatter.Reputation(self.getReputation())
        
        self.canGiveKarma()
        sdb["karma_given"] = str(self.karma_given)
        
        tdelta = datetime.datetime.now() - self.karma_time
        sdb["karma_given_hours"] = str(int(tdelta.total_seconds() / (60*60)))
        
    
        BotWrappers.sendMessage(bot, self, s, sdb, parse_mode = "HTML")
                    
        

        