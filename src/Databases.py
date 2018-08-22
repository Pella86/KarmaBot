# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 21:12:18 2018

@author: Mauro
"""
#==============================================================================
# Imports
#==============================================================================

import os
import pickle

import Logging

#==============================================================================
# logging
#==============================================================================
# create logger
log = Logging.get_logger(__name__, "WARNING")

#==============================================================================
# Helper functions
#==============================================================================

def get_pathname(path):
    ''' Little function to split the path in path, name, extension'''
    path, nameext = os.path.split(path)
    name, ext = os.path.splitext(nameext)
    return path, name, ext

#==============================================================================
# Data class
#==============================================================================
class Data:
    
    def __init__(self, id, content):
        self.id = id
        self.content = content
        self.filename = None
        self.hasChanged = True
    
    def getData(self):
        return self.content
    
    def setData(self, content):
        self.content = content
        self.hasChanged = True
    
    def setId(self, id):
        self.id = id
        self.hasChanged = True

#==============================================================================
# Database class
#==============================================================================
class Database:
    
    
    def __init__(self, folder, data_name):
        
        self.folder = folder
        self.data_name = data_name
        self._db = {}
        
        self.short_uid = None
    
    def keys(self):
        return self._db.keys()

    def getUID(self):
        return self.short_uid
    
    def isNew(self, data_id):
        if data_id in self._db:
            return False
        else:
            return True
    
    def addData(self, data):
        self._db[data.id] = data
        filename = self.data_name + str(self.short_uid)
        self._db[data.id].filename = filename
        self._db[data.id].hasChanged = True
        self.short_uid += 1

    def update_uid(self):
        
        names = [data.filename for data in self._db.values()]
        
        last_uid = 0
        if names:
            uids = [int(name.split("_")[1]) for name in names]
            uids = sorted(uids)
            last_uid = uids[-1]
            log.debug("last uid:{}".format(last_uid))
        
        self.short_uid = last_uid + 1 
    
    def setItem(self, data):
        log.debug("data set " + str(data.id) + " : " + str(data.content))
        self._db[data.id].setData(data.content)
        
    def __getitem__(self, dataid):
        return self._db[dataid]
    
    def deleteItem(self, data):
        os.remove(os.path.join(self.folder, data.filename + ".pickle"))
        del self._db[data.id]
    
    def getValues(self):
        return [v.getData() for v in self._db.values()]

    def loadDB(self):
        log.debug("loading db...")
        files = [os.path.join(self.folder, f) for f in os.listdir(self.folder)]
        
        data_loaded = 0
        idlist = []
        for file_name in files:
            _, _, ext = get_pathname(file_name)
            if ext == ".pickle" and os.path.isfile(file_name):
                # Open file
                with open(file_name, 'rb') as f:
                    data = pickle.load(f)
                
                # check in case there are mistakes
                if data.id in idlist:
                    log.debug("duplicate file found")
                    os.remove(file_name)
                else:
                    # load the data in memory
                    self._db[data.id] = data
                    idlist.append(data.id)
                    data_loaded += 1
        
        log.info("Loaded {} data".format(data_loaded))
    
    def writeData(self, data):
        filename = os.path.join(self.folder , data.filename + ".pickle")
        with open(filename, "wb") as f:
            pickle.dump(data, f)   
            
    def saveDB(self):
        for data in self._db.values():
            self.writeData(data)
    
    def updateDB(self):
        for data in self._db.values():
            if data.hasChanged:
                data.hasChanged = False
                self.writeData(data)
                log.info("database update!")
                
    def updateDatabaseEntry(self, attributes, success_file = ""):
        log.debug("updating attributes")

        if os.path.isfile(success_file):
            raise Exception("File already exist")
            
        for delement in self._db.values():
            element = delement.getData()
            
            for attr_name, attr_value in attributes.items():
                
                log.debug("attribute {} : calculated value {}".format(attr_name, attr_value(element)))
                
                element.__setattr__(attr_name, attr_value(element))
            
            delement.setData(element)
        
        self.updateDB()
        
        if success_file:
            with open(success_file, "w") as f:
                f.write("success: " + self.folder)                
            
## usage example
#    categories.categories_db.updateDatabaseEntry({"screen_name": lambda x : x.name, "creation_date": lambda x : datetime.datetime.now()}, "./data/categories_update_success.txt")            
        
        
        
        