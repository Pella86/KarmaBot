# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 21:37:49 2018

@author: Mauro
"""

#==============================================================================
# Imports
#==============================================================================

import hashlib

import Databases
import Logging

#==============================================================================
# logging
#==============================================================================
# create logger
log = Logging.get_logger(__name__, "WARNING")

#==============================================================================
# Persons databases
#==============================================================================
class PersonDB:
    
    def __init__(self):
        folder = "./databases/persons_db"
        self.database = Databases.Database(folder, "person_")
        self.database.loadDB()
        self.database.update_uid()
        log.info("loaded persons db")

    
    def addPerson(self, person):
        # hash the id
        pid = hashlib.sha256()
        pid.update(bytes(person.id))
        
        hash_id = pid.digest()
        
        if self.database.isNew(hash_id):
            log.info("added new person to database: {}".format(self.database.short_uid))
            data = Databases.Data(hash_id, "place holder")
            self.database.addData(data)
    
    def update(self):
        log.info("updating database...")
        self.database.updateDB()

if __name__ == "__main__":
    print("hi")