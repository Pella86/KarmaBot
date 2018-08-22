# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 12:10:14 2018

@author: Mauro
"""
#==============================================================================
# Imports
#==============================================================================
# py imports
import os
import hashlib
import string

# my imports
import Databases
import UserProfile
import random
import Logging

#==============================================================================
# logging
#==============================================================================
# create logger
log = Logging.get_logger(__name__, "WARNING")

#==============================================================================
# Helpers
#==============================================================================
def get_hash_id(personid):
    pid = hashlib.sha256()
    pid.update(bytes(personid))
    
    return pid.digest()   

allowed_nickname_characters = string.ascii_letters + string.digits + "@"

def check_nickname(username):
    for letter in username:
        if letter not in allowed_nickname_characters:
            return False
    return True

def pick_username(person):
    if person.username and len(person.username) < 15 and check_nickname(person.username):
        return person.username
    elif person.first_name and len(person.first_name) < 15 and check_nickname(person.username):
        return person.first_name    
    else:
        return None

#==============================================================================
# User database
#==============================================================================
class UsersDB:
    
    def __init__(self):
        self.folder = "./databases/user_db"
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)
        
        self.database = Databases.Database(self.folder, "user_")
        self.database.loadDB()
        self.database.update_uid()
        log.info("loaded users database")

        folder = "./databases/banned_user_db"
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        self.banned_database = Databases.Database(folder, "banned_user_") 
    
    def getUsersList(self):
        return self.database.getValues()
    
    
    def banUser(self, user):
        duser = self.database[user.hash_id]
        self.deleteUser(duser)
        

    def addUser(self, person, chatid):
        # hash the id

        hash_id = get_hash_id(person.id)
        
        if self.database.isNew(hash_id):
            log.info("added new user to database: {}".format(self.database.short_uid))
            
            display_id = pick_username(person)
            if not display_id:
                # create a unique display id
                start_number = 0x10000000
                stop_number = 0xFFFFFFFF
                display_id = hex(random.randint(start_number,stop_number)).upper()[2:]
                log.debug("display id {}".format(display_id))


            
            # check for uniqueness
            display_id_list = [user.display_id for user in self.database.getValues()]
            while display_id in display_id_list:
                display_id = hex(random.randint(start_number,stop_number)).upper()[2:]
                log.debug("new display id {}".format(display_id))                
            
            # language
            lang_tag = person.language_code if person.language_code else "en"

            # user instance
            user = UserProfile.UserProfile(hash_id, display_id, chatid, lang_tag)
            data = Databases.Data(hash_id, user)
            self.database.addData(data)
    
    def deleteUser(self, user):
        data = self.database[user.hash_id]
        self.database.deleteItem(data)
    
    def hGetUser(self, hash_id):
        return self.database[hash_id].getData()
        
    def getUser(self, person):
        log.debug("User already in database, got user")
        hash_id = get_hash_id(person.id)
        return self.database[hash_id].getData()
    
    def setUser(self, user):
        self.database[user.hash_id].setData(user)

    def update(self):
        log.info("updating database...")
        self.database.updateDB()
        
        
        