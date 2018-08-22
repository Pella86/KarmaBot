# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:27:02 2018

@author: Mauro
"""
import EmojiTable

#def suffix_numbers(num, prec):
#    magnitude = 0
#    onum = num
#    while abs(num) >= 1000:
#        magnitude += 1
#        num /= 1000.0
#        if magnitude >= 5:
#            break
#
#    if abs(onum) <= 999:
#        return '{0}'.format(num)
#    else:
#        suffix_list = ('', 'K', 'M', 'G', 'T', 'P')
#        format_pattern = '{0:.' + str(prec) + 'f}{1}'
#        return format_pattern.format(num, suffix_list[magnitude])

suffix_list = ('', 'K', 'M', 'G', 'T', 'P')
    
def suffix_numbers(num, prec):
    magnitude = 0
    onum = num
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
        if magnitude >= 5:
            break
    if abs(onum) <= 999:
        return num, None
    else:
        return num, suffix_list[magnitude]




class FormatNumber:
    
    def __init__(self, number, precision = 2, symbol = None, sufffixed = True):
        self.number = number
        self.suffixed = sufffixed
        self.precision = precision
        self.symbol = symbol
    
    
    def __str__(self):
        value = None
        
        if self.suffixed:
            value, suffix = suffix_numbers(self.number, self.precision)
        
        if self.precision == 0:
            format_pattern = "{:d}"
            value = format_pattern.format(int(value))
        else:
            format_pattern = "{:." + str(self.precision) + "f}"
            value = format_pattern.format(value)
        
        if suffix:
            value += suffix
    
        if self.symbol:
            value += self.symbol
        
        return value

class PellaCoins(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
        super().__init__(number, precision, EmojiTable.points_emoji, suffixed)


class Karma(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
        super().__init__(number, precision, EmojiTable.karma_emoji, suffixed)


class Reputation(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
        super().__init__(number, precision, EmojiTable.reputation_emoji, suffixed)

class RepPoints(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
        super().__init__(number, precision, EmojiTable.reputation_points_emoji, suffixed)
        
class UpVotes(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
      super().__init__(number, precision, EmojiTable.upvote_emoji, suffixed)  


class DownVotes(FormatNumber):
    
    def __init__(self, number, precision = 0, suffixed = True):
      super().__init__(number, precision, EmojiTable.downvote_emoji, suffixed)  