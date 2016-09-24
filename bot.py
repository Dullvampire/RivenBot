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
import time
import _thread as thread

import inspect
import sched
from sympy import *

TOKEN = 'MjI4MDM1MzEwMTM3NzcwMDA0.CsO18g.WNtn1y805SsVfevSp4WsA_nGZtE'
SYSTEM_ADMIN = 186185272302501888

class Out:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode

        self._printDef = sys.stdout
        sys.stdout = self

    def write(self, x):
        f = open(self.path, self.mode)
        s = str(x)
        f.write(s)
        self._printDef.write(s)

        f.close()

    def flush(self):
        pass

    def clear(self):
        f = open(self.path, 'w')

        f.write('')

        f.close()


Out('log.txt', 'a')


class Command:  # Generic class for all commands, handles parsing
    def __init__(self, name, description, function, args={}, requiresAdmin = False):
        self._name = name
        self._description = description
        self._args = args
        self._function = function

        self._reqAdmin = requiresAdmin

        if self._args != -1: #-1 signifies that this command doesnt get split
            argCount = 0

            for i in inspect.getargspec(self._function)[0]:
                if i != 'self':
                    argCount += 1

            if argCount != len(args.keys()):
                raise ValueError('Expected %i arguments, got %i in command %s' %
                                 (len(args.keys()), len(self._args.keys()), self._name))

    def __call__(self, s):
        # Calls the command from a string, String contains
        # only the args, the original command section was
        # left out, for example:
        # *{command} {arg1} {arg2} ... {argn}
        # only {arg1} {arg2} ... {argn} is included
        if self._args != -1:
            s = s.split(' ')

            for i in s:
                if i == '':
                    s.remove(i)

            if len(s) != len(self._args.keys()):
                raise ValueError('Expected %i arguments, got %i in command %s' %
                                 (len(self._args.keys()), len(s), self._name))
        # Calls given function with args after being called by the function to convert arg
            return self._function(*map(lambda a: self._args[a[0]](a[1]),
                                       zip(self._args, s)))

        else:
            return self._function(s)

    def name(self):
        return self._name

    def description(self):
        return self._description

    def requiresAdmin (self):
        return self._reqAdmin


class MusicPlayer:
    def __init__ (self, client, master):
        self.queue = []
        self.client = client

        self.master = master

        self.scheduler = sched.scheduler(time.time, time.sleep)

    def addToQueue (self, url):

        player = yield from self.client.create_ytdl_player(url, after = self.playNext)

        self.queue.append(player)

        if len(self.queue) == 1:
            self.playNext()

    def playNext (self):
        if len(self.queue) > 0:
            if self.queue[0].is_done():
                self.queue.pop(0)
            self.queue[0].start()


    def pause (self):
        if len(self.queue) > 0:
            self.queue[0].pause()

    def resume (self):
        if len(self.queue) > 0:
            self.queue[0].resume()

    def skip (self):
        if len(self.queue) > 0:
            self.queue[0].stop()

    def stop (self):
        if self.isPlaying(): self.queue[0].stop()

        self.queue = []

    def isPlaying (self):
        if len(self.queue) > 0:
            return self.queue[0].is_playing()

        return False

class MyClient(discord.Client):
    def init(self, start):
        sys.stdout.clear()

        self.commandStart = start
        self.commands = {}
        self.commandLocals = {}

        self.players = {}

        return self

    def addCommand(self, *arg, **kwarg):
        if arg[0] not in self.commands:
            c = Command (*arg, **kwarg)
            self.commands[arg[0]] = c
            return c

        else:
            raise ValueError ('Command %s already exists' % name)

    @asyncio.coroutine
    def on_ready(self):
        print('Login Successful')

    @asyncio.coroutine
    def on_message(self, message):
        self.commandLocals['message'] = message
        # Don't want to do anything if the sender is client
        if message.author != self.user:
            yield from self.parseCommand(message.content)

        self.commandLocals = {}

    def parseCommand(self, s):
        s = s.split(' ')
        if len(s) > 0:
            for i in self.commands.keys():
                if s[0] == self.commandStart + i:
                    command = self.commands[i]
                    do = True
                    if command.requiresAdmin() and not self.isAdmin(self.loc('message').author):
                        do = False

                    if do:
                        r = command(' '.join(s[1 : ]))

                        if r == None:
                            r = []

                        yield from r

    def isAdmin (self, user):
        return str(SYSTEM_ADMIN) == user.id

    def joinChannel (self):
        message = self.loc('message')

        for channel in message.server.channels:
            if message.author in channel.voice_members:
                voiceClient = yield from self.join_voice_channel(channel)
                self.players[message.server.id] = MusicPlayer(voiceClient, self)
                return voiceClient

        return []

    def leaveChannel (self):
        message = self.loc('message')

        self.players[message.server.id].stop()
        yield from self.players[message.server.id].client.disconnect()

        del self.players[message.server.id]

        return []

    def play (self, url):
        message = self.loc('message')
        if message.server.id not in self.players.keys():
            yield from self.joinChannel()

        yield from self.players[message.server.id].addToQueue(url)

    def pause (self):
        message = self.loc('message')
        yield from self.players[message.server.id].pause()

    def resume(self):
        message = self.loc('message')
        yield from self.players[message.server.id].resume()

    def skip (self):
        message = self.loc('message')
        yield from self.players[message.server.id].skip()

    def root (self, equ):
        solution = solve(equ, Symbol('x'))
        f = open('root.txt', 'w')
        f.write(pretty(solution, use_unicode = False))
        f.close()
        yield from self.send_file(self.loc('message').channel, 'root.txt')

    def gcd (self, s):
        s = s.replace(',', '')
        try:
            ns = sorted(list(map(int, s.split(' ')))) #Turns the given string into ints
        except:
            print('Error with input %s in function MyClient.gcd' % s)
            yield from self.send_message(self.loc('message').channel, 'Please format your input in the form \n' +
                                                                      ' *gcd {num1} {num2} ... {numn}')
        result = ns[0]

        for i in ns[ 1 : ]:
            result = _gcd(result, i)

        #This mess formats the message and sends it
        yield from self.send_message(self.loc('message').channel,
                                     ('The greatest common factor of %s is %i, if you were factoring the result will be %s'
                                      % (s, result, ' '.join(list(map(lambda x: str(int(x) // result), s.split(' ')))))))

    def restart (self):
        print('Attempting to restart')
        self.logout()
        thread.start_new_thread(os.system, ('bot.py',))
        sys.tracebacklimit = 0
        raise

    def help (self, s):
        f = ''
        if s == '':
            for i in self.commands.keys():
                f += self.commands[i].name() + ' - ' + self.commands[i].description()\
                  + ' - Must be admin' * self.commands[i].requiresAdmin() + '\n'
        else:
            c = s.strip()
            f = self.commands[c].name() + ' - ' + self.commands[c].description()

        yield from self.send_message(self.loc('message').channel, f)

    def loc (self, key):
        return self.commandLocals[key]

def _gcd (a, b):
    if a < b:
        a, b = b, a

    while b != 0:
        a, b = b, a % b

    return a

def start ():
    client = MyClient().init('*')

    client.addCommand('join', 'Tells RivenBot to join your channel', client.joinChannel)
    client.addCommand('leave', 'Tells RivenBot to leave your channel', client.leaveChannel)
    client.addCommand('play', 'RivenBot plays a song', client.play, args = {'url' : str})
    client.addCommand('pause', 'Tells RivenBot to pause', client.pause)
    client.addCommand('resume', 'Tells RivenBot to resume', client.resume)
    client.addCommand('skip', 'Tells RivenBot to skip', client.skip)

    client.addCommand('root', 'RivenBot is good at math and will solve for the root of any equation!', client.root, args = -1)
    client.addCommand('gcf', 'RivenBot computes the greatest common divisor/factor of any numbers', client.gcd, args = -1)
    client.addCommand('gcd', 'gcf Alias', client.gcd, args = -1)

    client.addCommand('restart', 'Restarts RivenBot', client.restart, requiresAdmin = True)

    client.addCommand('help', 'RivenBot tells you about all her cool features', client.help, args = -1)

    print('Initialized Correctly')

    client.run('MjI4MDM1MzEwMTM3NzcwMDA0.CsO18g.WNtn1y805SsVfevSp4WsA_nGZtE')

start()