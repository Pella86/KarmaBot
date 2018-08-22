# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 09:25:16 2017

@author: Mauro
"""

import telepot

#from LogTimes import Logger
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fh = logging.FileHandler("./log_files/test_log.log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

log.addHandler(fh)
log.addHandler(logging.StreamHandler())


#from telepot.namedtuple import CallbackQuery

#import messages_examples as me

#import pprint

# could make a field class -> if has optionals -> init optionals


CHAT_MEMBER_TYPES = ["creator", "administrator", "member", "restricted", "left", "kicked"]
CHAT_TYPES =  ["private", "group", "supergroup", "channel"]
VALID_MEDIA = ["photo", "video", "document"]


class ChatMember:
    
    def __init__(self, chatmembermsg, bot = None, opt = True):
        
        # can create the chat member from the JSON dict       
        if type(chatmembermsg) is dict:
            self.ct_mem_msg = chatmembermsg
        elif type(chatmembermsg) is tuple and len(chatmembermsg) == 2:
            chatid = chatmembermsg[0]
            userid = chatmembermsg[1]
            self.ct_mem_msg = bot.getChatMember(chatid, userid)
        else:
            print("ChatMember: bad input format")
        
        # required fields
        self.person = Person(self.ct_mem_msg["user"])
        self.status = self.ct_mem_msg["status"]
        #optional fields
        if opt:
            self.initOptionals()
            
    def initOptionals(self):
        self.until_date = self.ct_mem_msg.get("untild_date")
        self.can_be_edited = self.ct_mem_msg.get("can_be_edited")
        self.change_info = self.ct_mem_msg.get("change_info")
        self.can_post_messages = self.ct_mem_msg.get("can_post_messages")
        self.can_edit_messages = self.ct_mem_msg.get("can_edit_messages")
        self.can_delete_messages = self.ct_mem_msg.get("can_delete_messages")
        self.can_invite_users = self.ct_mem_msg.get("can_invite_users")
        self.can_restrict_members = self.ct_mem_msg.get("can_restrict_members")
        self.can_pin_messages = self.ct_mem_msg.get("can_pin_mesasges")
        self.can_promote_members = self.ct_mem_msg.get("can_promote_members")
        self.can_send_media_messages = self.ct_mem_msg.get("can_send_media_messages")
        self.can_send_other_messages = self.ct_mem_msg.get("can_send_other_messages")
        self.can_add_web_page_previews = self.ct_mem_msg.get("can_add_web_page_previews")
        
    def __str__(self):
        return "User: {0}| Status: {1}".format(self.person, self.status)
        

class CbkQuery:
    
    def __init__(self, query_msg, opt = True):
        #required arguments
        self.id = query_msg['id']
        self.person = Person(query_msg['from'])
        self.chat_instance = query_msg['chat_instance']
        

        self.query_msg = query_msg
        self.init_opt = False
        if opt:
            self.initOptionals()
    
    def initOptionals(self):
        self.data = self.query_msg.get('data')
        self.message = self.query_msg.get('message')
        if self.message is not None:
            self.message = Message(self.message)
        self.inline_message_id = self.query_msg.get('inline_message_id')
        self.game_short_name = self.query_msg.get('game_short_name')
        self.init_opt = True
    
    
    def __str__(self):
        
        sdb = {}
        
        sdb['id'] = self.id
        sdb['person'] = self.person
        sdb['chat_inst'] = self.chat_instance
        sdb['data'] = self.data
        sdb['message'] = self.message
        sdb['imsg_id'] = self.inline_message_id
        sdb['gsname'] = self.game_short_name
        
        s = "id: {id}|person: {person}|chat: {chat_inst}|data: {data}|msg: {message}|imsgid: {imsg_id}|gsname:{gsname}".format(**sdb) 
        return s
    
    def getChatMsgID(self):
        # returns the tuple needed to modify the message
        if not self.init_opt:
            self.initOptionals()
        return (self.message.chat.id, self.message.message_id)

class Person:
    
    def __init__(self, msg, opt = True):
        self.id = msg['id']
        self.first_name = msg["first_name"]
        
        self.msg = msg
        self.init_opt = False
        if opt:
           self.initOptionals() 

    def initOptionals(self):
        self.username = self.msg.get('username')
        self.language_code = self.msg.get('language_code')  
        self.last_name = self.msg.get('last_name')
        self.init_opt = True
    
    def info(self):
        if len(self.first_name) > 10:
            sname = self.first_name[:7] + "..."
        else:
            sname = self.first_name
        
        return "{0}(@{1})".format(sname, self.username)
        
    
    def __str__(self):
        return self.info()

class Chat:
    
    def __init__(self, chat):
        self.id = chat["id"]
        self.type = chat["type"]
        
        if self.type == "private":
            self.person = Person(chat)

        if self.type == "supergroup":
            self.title = chat["title"]
    
    def info(self):
        description = ""
        if self.type == "supergroup":
            description += self.title
        
        if self.type == "private":
            description += self.person.info()
            
        return "{0} | {1}".format(self.type, description)

    def __str__(self):
        return self.info()


class Content:
    
    def __init__(self, content_msg, content_type):
        self.type = content_type
        self.file_id = content_msg['file_id']
    
    def info(self):
        return "{0} id: {1}".format(self.type, self.file_id)
    
    def __str__(self):
        return self.info()


class Photo(Content):
    
    def __init__(self, photo):
        super().__init__(photo, "photo")
        
        
        self.width = photo["width"]
        self.height = photo["height"]
        
        self.file_path = None
        self.file_size = None

        try:
            self.file_size = photo["file_size"]
        except KeyError:
            pass
        
        try:
            self.file_path = photo["file_path"]
        except KeyError:
            pass
    
    def info(self):
        return "Picture size {0}x{1}".format(self.width, self.height)

    def __str__(self):
        return self.info()

class Sticker(Content):
    
    def __init__(self, sticker, opt=False):
        super().__init__(sticker, "sticker")
        
        self.width = sticker['width']
        self.height = sticker['height']
        self.original = sticker
        self.init_opt = False
        if opt:
            self.initOptionals()
    
    def initOptionals(self):
        self.emoji = self.original.get('emoji')
        self.set_name = self.original.get('set_name')
        self.thumb = Photo(self.original.get('thumb'))
        self.file_size = self.original.get('file_size')
        self.init_opt = True
    
    def info(self):
        return "Sticker from {0} pack with emoji {1}".format(self.set_name, self.emoji)
    
    def __str__(self):
        return self.info()
              
class Video(Content):
    
    def __init__(self, video):
        super().__init__(video, "video")
        
        self.duration = video["duration"]
        self.width = video["width"]
        self.height = video["height"]
        self.mime_type = video["mime_type"]
        self.thumb = Photo(video["thumb"])
       
        self.file_size = video.get("file_size")
     
    def info(self):
        return "{0}s video type {1}".format(self.duration, self.mime_type)

    def __str__(self):
        return self.info()

class Document(Content):
    
    def __init__(self, document):
        super().__init__(document, "document")
        
        
        self.mime_type = document["mime_type"]
        self.file_size = document.get("file_size")
        self.thumb = None
        self.file_name = document.get("file_name")
        
        try:
            self.thumb = Photo(document["thumb"])
        except KeyError:
            pass
        
    
    def info(self):
        return "Document {0}".format(self.mime_type)
    
    def __str__(self):
        return self.info()
    
class Text(Content):
    
    def __init__(self, text):
        dummy = {}
        dummy["file_id"] = None
        super().__init__(dummy, "text")
        
        self.text = text

    def info(self):
        return self.text
    
    def __str__(self):
        return self.info()    

class Photos(Content):
    
    def __init__(self, photos):
        super().__init__(photos[0], "photo")
        
        self.photos = [ Photo(pic) for pic in photos ]
    
    def info(self):
        return self.photos[0].info()
    
    def __str__(self):
        return self.info()

class Voice(Content):
    
    def __init__(self, msg, opt = False):
        super().__init__(msg, "voice")
        
        self.duration = msg["duration"]
        
        self.original = msg
        self.init_opt = False
        if opt:
            self.initOptionals()
    
    def initOptionals(self):
        self.mime_type = self.original.get("mime_type")
        self.file_size = self.original.get("file_size")
        self.init_opt = True

class VideoNote(Content):
    
    def __init__(self, msg, opt = False):
        super().__init__(msg, "video_note")
        
        self.length = msg["length"]
        self.duration = msg["duration"]
        
        self.original = msg
        self.init_opt = False
        if opt:
            self.initOptionals()
    
    def initOptionals():
        raise Exception("Not implemented")
        # to do implement shit

class Audio(Content):
    
    def __init__(self, msg, opt = False):
        super().__init__(msg, "audio")
        
        self.duration = msg["duration"]

        self.original = msg        
        self.init_opt = False
        if opt:
            self.initOptionals()
 
    def initOptionals():
        raise Exception("Not implemented")
        # to do implement shit
    
        
        

    

class Message:
    
    def __init__(self, msg, opt = True):

        self.original = msg
        
        self.message_id = msg["message_id"]
        self.chat = Chat(msg["chat"])
        self.date = msg["date"]
        
        
        self.init_opt = False
        if opt:
            self.initOptionals()
    
    def initOptionals(self):
        self.mfrom = self.original.get("from")
        if self.mfrom is not None:
            self.mfrom = Person(self.mfrom)
        
        self.fw_from = self.original.get('forward_from')
        if self.fw_from is not None:
            self.fw_from = Person(self.fw_from)
        
        self.fw_from_chat = self.original.get('forward_from_chat')
        if self.fw_from_chat is not None:
           self.fw_from_chat = Chat(self.fw_from_chat) 
          
        self.fw_msg_id = self.original.get('forward_from_message_id')
        self.fw_date = self.original.get('forward_date')

        
        self.reply = self.original.get('reply_to_message')
        if self.reply is not None:
            self.reply = Message(self.reply)
            
        self.date = self.original.get('edit_date')
        
        
        
        content_type, _, _ = telepot.glance(self.original)
        self.content_type = content_type
        self.known_content = ["text", "photo", "new_chat_member", "sticker",
                              "video", "document", "voice", "video_note", "audio"]
        
        
        self.content = None
        
        if self.content_type == "text":
            self.content = Text(self.original["text"])
            
        if self.content_type == "photo":
            self.content = Photos(self.original["photo"])

        if self.content_type == "sticker":
            self.content = Sticker(self.original["sticker"])
        
        if self.content_type == "video":
            self.content = Video(self.original["video"])
        
        if self.content_type == "document":
            self.content = Document(self.original["document"])
        
        if self.content_type == "voice":
            self.content = Voice(self.original["voice"])
        
        if self.content_type == "video_note":
            self.content = VideoNote(self.original["video_note"])
            
        if self.content_type == "audio":
            self.content = Audio(self.original["audio"])

        if self.content_type == "new_chat_member":
            self.new_chat_participant = Person(self.original["new_chat_participant"])
            self.new_chat_member = Person(self.original["new_chat_member"])
            self.new_chat_members = [Person(person) for person in self.original["new_chat_members"]]
            
        self.init_opt = True
        
    
    def info(self):
        
        if self.reply is not None:
            reply = "Reply to " + self.reply.mfrom.info() + "\n"
        else:
            reply = ""
            
        if self.fw_from is not None:
            forward = "Forwarded from " + self.fw_from.info() + "\n"
        else:
            forward = ""
            
        return reply + forward + "Message ({0}) from: {1}".format(
                self.content_type, 
                self.mfrom.info()
                )
    
    def print_content(self):
        s = ""
        if self.content_type == "text":
            s += self.content.text
        elif self.content_type in ["sticker", "video","document", "photo"] :
            s += self.content.info()
        else:
            s += "message content not supported"
        return s

    def __str__(self):
        return "mID: {0}|Chat: {1}|date: {2}".format(self.message_id, self.chat, self.date)

class InlineQuery:
    
    def __init__(self, msg):
        self.original = msg
        
        self.mfrom = self.original["from"]
        self.mfrom = Person(self.mfrom)
        
        self.id = msg["id"]
        self.offset = msg["offset"]
        self.query = msg["query"]

class InlineResult:
    
    def __init__(self, msg):
        self.original = msg
        
        self.mfrom = self.original["from"]
        self.mfrom = Person(self.mfrom)
        
        self.query = msg["query"]  
        self.result_id = msg["result_id"]

if __name__ == "__main__":
    
    msg = me.sticker_message
    
    print(" ORIGINAL MESSAGE ")
    
    print(msg)
    
    print("\n MY MESSAGE ")

    
    for i in range(100000):
        qmsg = Message(msg, opt=False)
    
    for i in range(100000):
        qmsg = Message(msg)
    
    print(qmsg)
    
    
    
    