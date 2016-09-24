# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 17:37:18 2016
https://discordapp.com/oauth2/authorize?client_id=228035310137770004&scope=bot&permissions=12659727
@author: Dante
"""

import discord

import asyncio

import os
import sys

import _thread as thread

TOKEN = 'MjI4MDM1MzEwMTM3NzcwMDA0.CsO18g.WNtn1y805SsVfevSp4WsA_nGZtE'

class Command: #Generic class for all commands, handles parsing
    def __init__ (self, name, description, function, args = {}):
        self._name = name
        self._description = description
        self._args = args
        self._function = function
    
    def __call__ (self, s): #Calls the command from a string, String contains
                            #only the args, the origninal command section was
                            #left out, for example:
                            #*{command} {arg1} {arg2} ... {argn}
                            #only {arg1} {arg2} ... {argn} is included
        s = s.split(' ')
        
        if len(s) != len(self._args.keys()):
            raise ValueError('Expected %i arguments, got %i in command %s' %
                            (len(s), len(self._args.keys()), self._name))
        #Calls given function with args after being called by the function to convert arg
        return self._function(*map(lambda a: self._args[a[0]](a[1]),  
                                   zip(self._args, s)))
    
    def name (self):
        return self._name
    
    def description (self):
        return self._description

class MyClient (discord.Client):
    @asyncio.coroutine   
    def on_message(self, message):
        "Asynchronous event handler that's called every time a message is seen by the user"
        print('Message received\n ', message.content)

if __name__ == '__main__':
    client = discord.Client()
    
    client.run('MjI4MDM1MzEwMTM3NzcwMDA0.CsO18g.WNtn1y805SsVfevSp4WsA_nGZtE')