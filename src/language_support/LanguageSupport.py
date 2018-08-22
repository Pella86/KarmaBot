# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 23:35:28 2018

@author: Mauro
"""

#==============================================================================
# Imports
#==============================================================================

import os
import logging
import datetime
import re
#==============================================================================
# Logging
#==============================================================================

# create logger
log = logging.getLogger(__name__)

# set logger level
log.setLevel(logging.INFO)

# create a file handler
fh = logging.FileHandler("./log_files/log_" + datetime.datetime.now().strftime("%y%m%d") + ".log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# create console and file handler
log.addHandler(fh)
log.addHandler(logging.StreamHandler())

#==============================================================================
# Translator
#==============================================================================

class Translator:
    
    def __init__(self):
        self.folder = "./languages"
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)
        
        self.encoding = "UTF-8"
        
        self.lang_tags = []
        
        self.tags_file = os.path.join(self.folder, "langauge_tags.txt")
        if not os.path.isfile(self.tags_file):
            with open(self.tags_file, "wb") as f:
                f.write("".encode(self.encoding))       
        
        
        self.langtostr = {} # key is (language-tag, string)
        
        self.reference_strings = []
        
        self.reference_file = os.path.join(self.folder, "reference_file.txt")
        if not os.path.isfile(self.reference_file):
            with open(self.reference_file, "wb") as f:
                f.write("".encode(self.encoding))
        
        self.lang_files = []
        self.files_to_tags = {}
        
        self.init()

    def init(self):
        # read the tags
        log.debug("initializing tags...")
        if os.path.isfile(self.tags_file):
            # read the tags
            with open(self.tags_file, "r") as f:
                lines = f.readlines()
            
            self.lang_tags = [line.strip() for line in lines]
        log.debug("tags: {}".format(len(self.lang_tags)))
        
        # list all the translation files
        log.debug("initializing filenames...")
        self.lang_files = []
        for tag in self.lang_tags:
            self.lang_files.append(self.getLangFileName(tag))
            self.files_to_tags[self.getLangFileName(tag)] = tag
        log.debug("Files: {}".format(len(self.lang_files)))
        
        # list all the known strings
        log.debug("initializing reference file...")
        with open(self.reference_file, "rb") as f:
            ref_content = f.read().decode(self.encoding)
        
        sent_pat = re.compile("--- new string ---")
            
        idxref = list(sent_pat.finditer(ref_content))
        
        for i, pat in enumerate(idxref):
            idx_start = pat.end() + 1
            if i == len(idxref) - 1:
                idx_end = len(ref_content)
            else:
                idx_end = idxref[i + 1].start()
            
            s = ref_content[idx_start: idx_end]
            self.reference_strings.append(s)
        log.debug("retrived strings: {}".format(len(self.reference_strings)))
        
        # read the blocks
        self.readLanguageFiles()
    
    def readBlocks(self, file):
        log.debug("reading blocks..")
        
        with open(file, "rb") as f:
            file_content = f.read().decode(self.encoding)
        
        english_pat = re.compile("--- English ---")
        translation_pat = re.compile("--- Translation ---")
        
        idx_en = list(english_pat.finditer(file_content))
        idx_tr = list(translation_pat.finditer(file_content))

        for i, x in enumerate(zip(idx_en, idx_tr)):
            enblock, trblock  = x
            # enblock
            idx_start = enblock.end() + 1
            
            idx_end = trblock.start() - 1 
            
            en_str = file_content[idx_start : idx_end]
            
            idx_start = trblock.end() + 1
            if i == len(idx_en) -1 :
                idx_end = len(file_content) - 1
            else:
                idx_end = idx_en[i + 1].start() - 2 
            tr_str =  file_content[idx_start : idx_end]
            tr_str = tr_str if tr_str else None
                  
            key = (en_str, self.files_to_tags[file])
            self.langtostr[key] = tr_str
                
    
    def readLanguageFiles(self):
        log.debug("Reading language files...")
        for file in self.lang_files:
            self.readBlocks(file)

    def getTagFolder(self, lang_tag):
        return os.path.join(self.folder, "language_" + lang_tag)

    def getLangFileName(self, lang_tag):
        folder = self.getTagFolder(lang_tag)
        file = "translation_file_" + lang_tag + ".tr"
        return os.path.join(folder, file)
    
    def updateTags(self, lang_tag):
        
        with open(self.tags_file, "a") as f:
            f.write(lang_tag + "\n")
            
        self.lang_tags.append(lang_tag)

        os.mkdir(self.getTagFolder(lang_tag))

        if not os.path.isfile(self.getLangFileName(lang_tag)):
            with open(self.getLangFileName(lang_tag), "wb") as f:
                f.write("".encode(self.encoding))
                
        self.lang_files.append(self.getLangFileName(lang_tag))
        self.files_to_tags[self.getLangFileName(lang_tag)] = lang_tag
        
        for string in self.reference_strings:
            self.addBlock(self.getLangFileName(lang_tag), string)
    
    def addBlock(self, file, string):
        block = "\n--- English ---\n".encode(self.encoding)
        block += string.encode(self.encoding)
        block += "\n--- Translation ---\n".encode(self.encoding)
        block += "\n".encode(self.encoding)
        with open(file, "ab") as f:
            f.write(block)
        
        key = (string, self.files_to_tags[file])
        self.langtostr[key] = None

    
    def addNewString(self, string):
        
        # add to reference
        with open(tr.reference_file, "ab") as f:
            s = "--- new string ---\n" + string
            f.write(s.encode(tr.encoding))
        self.reference_strings.append(string)
        
        # add to other files as translation bloc
        for file in self.lang_files:
            self.addBlock(file, string)
    

#==============================================================================
# Initialize global translator     
#==============================================================================
        
tr = Translator()

#==============================================================================
# Translate function
#==============================================================================

def _(string, lang_tag):
    log.debug("translating string...")
    
    if lang_tag not in tr.lang_tags:
        log.debug("updating lang tags...")

        tr.updateTags(lang_tag)
        
        if len(lang_tag) == 5:
            new_tag = lang_tag[0 : 2]
            tr.updateTags(new_tag)

    if string not in tr.reference_strings:
        log.debug("add new string...")
        # append the string to the reference
        tr.addNewString(string)
    
    key = (string, lang_tag)
    
    translation = tr.langtostr[key]
    
    if translation is None:
        # try 
        key = (string, lang_tag[0:2])
        translation = tr.langtostr[key]
        
        if translation is None:
            translation = string
    
        
    return translation