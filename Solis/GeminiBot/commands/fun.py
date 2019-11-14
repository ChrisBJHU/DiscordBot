import asyncio
import threading
import time
from multiprocessing import Process
from random import randint, random
import math
import cat
import os
import hashlib

import xlrd
from discord.ext import commands
from utils.tools import *
from utils.unicode import *
from utils.fun.lists import *
from utils.fun.fortunes import fortunes
from utils import imagetools
from PIL import Image
from utils.language import Language
from threading import Thread


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    game = ''
    awaitingquestion = 0
    memberrole = ''
    correct = False
    start = 0
    timercounter = 0
    bot = ''
    role = ''
    role1 = ''

    @commands.command()
    async def start(self, ctx):
        """Starts the Science Bowl Contest."""
        if self.awaitingquestion == 1:
            await ctx.send('Already started the game.')

    @commands.command(aliases=['end'])
    async def exit(self, ctx):
        """Stops the Science Bowl Contest."""
        if self.awaitingquestion != 1:
            await ctx.send('Not currently running the game.')

    @commands.command()
    async def skipQ(self, ctx):
        """Skips the current Science Bowl Question."""
        if self.awaitingquestion != 1:
            await ctx.send('Not currently running the game.')

    @commands.command(aliases=['scores'])
    async def points(self, ctx):
        """Obtain current points for the contest."""
        if self.awaitingquestion != 1:
            await ctx.send('Not currently running the game.')

    def __init__(self, bot):
        self.bot = bot

    async def check(self, message):
        user = message.author
        self.role = discord.utils.get(user.roles, name="A")
        self.role1 = discord.utils.get(user.roles, name="B")
        if self.role in message.author.roles or self.role1 in message.author.roles:
            if self.role in message.author.roles:
                self.memberrole = self.role
            if self.role1 in message.author.roles:
                self.memberrole = self.role1
        if message != '':
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        global response
        if message.author.id == self.bot.user.id:
            return
        await self.check(message)
        if self.role in message.author.roles or self.role1 in message.author.roles:
            if message.content.startswith('.start') and self.awaitingquestion != 1:
                self.game = Start()
                self.awaitingquestion = 1
                response = self.game.sg(self.role, self.role1)
                await message.channel.send('\nToss Up:\n------------------')
                time.sleep(2)
                await message.channel.send(response)
                self.start = time.time()

            elif self.awaitingquestion == 1:
                if message.content.startswith('.exit') or message.content.startswith('.end'):
                    await message.channel.send('Game Ended.')
                    time.sleep(2)
                    await message.channel.send('\nScoreboard:\n---------------------\n')
                    time.sleep(2)
                    await message.channel.send(str(self.game.TeamScoreA()) + '\n\n' + str(self.game.TeamScoreB()))
                    self.awaitingquestion = 0
                    self.start = ''
                    self.game = ''

                elif message.content.startswith('.points') or message.content.startswith('.scores'):
                    await  message.channel.send(
                        '\nScoreboard:\n---------------------')
                    await message.channel.send(
                        '\n\n' + str(self.game.TeamScoreA()) + '\n \n' + str(self.game.TeamScoreB()))

                elif message.content.startswith('.skipQ'):
                    await message.channel.send('Skipping Current Question...')
                    time.sleep(2)
                    response = self.game.play()
                    self.start = time.time()
                    await message.channel.send(response)

                elif time.time() - self.start > 10 and self.timercounter == 0:
                    self.timercounter = 1
                    await message.channel.send(
                        'Time ran out.\nAnswer was:\n' + str(
                            self.game.getAnswer()) + '\nIf a team was correct, they must '
                                                     'respond to this with y or n to fix '
                                                     'scores and return next question.')

                elif (message.content.lower() == 'y' or message.content.lower() == 'n') and self.timercounter == 1:
                    self.timercounter = 0
                    if message.content.lower()[:1] == 'y':
                        self.game.FixCheck(self.memberrole)
                        if self.game.ChangeQuestion():
                            self.game.fixScores(self.memberrole)
                            await message.channel.send('\nBonus:\n------------------')
                            response = self.game.getBonus()
                        else:
                            await message.channel.send('\nToss Up:\n------------------')
                            response = self.game.play()
                    else:
                        await message.channel.send('\nToss Up:\n------------------')
                        response = self.game.play()
                    time.sleep(3)
                    self.start = time.time()
                    await message.channel.send(response)

                elif self.timercounter == 0:
                    if self.role in message.author.roles or self.role1 in message.author.roles:
                        self.correct = self.game.answer(message.content, self.memberrole)
                        if not self.correct and self.correct is not None:
                            await message.channel.send('Your answer was incorrect.')
                        elif self.correct:
                            self.game.FixCheck(self.memberrole)
                            await message.channel.send(
                                str(self.memberrole) + ' got the question correct!\n------------------\n')
                            if self.game.ChangeQuestion():
                                self.game.fixScores(self.memberrole)
                                await message.channel.send('\nBonus:\n------------------')
                                response = self.game.getBonus()
                            else:
                                await message.channel.send('\nToss Up:\n------------------')
                                response = self.game.play()
                            time.sleep(3)
                            self.start = time.time()
                            await message.channel.send(response)


def setup(bot):
    bot.add_cog(Fun(bot))


class Question:
    Category = ''
    Type = ''
    Format = ''
    AnswerChoices = ''
    Question = ''
    CorrectAnswer = ''

    def __init__(self, A, B, C, D, E, F):
        self.Category = A
        self.Type = B
        self.Format = C
        self.AnswerChoices = D
        self.Question = E
        self.CorrectAnswer = F

    def toStringA(self):
        return str(self.Category) + '\n' + str(self.Type) + '\n' + str(self.Format) + '\n' + str(
            self.Question) + '\n' + self.SplitN(str(self.AnswerChoices))

    def SplitN(self, n):
        n = str(n)
        b = n.split('\c')
        c = 'Answer Choices: \n'
        for x in b:
            c += x + '\n'
        return c

    def checkAnwser(self):
        return self.CorrectAnswer

    def checkAsA(self, A):
        if self.CorrectAnswer.lower() in A.lower():
            return True
        return False


class Start:
    loc = ''
    index = 0
    Q = ''
    n = ''
    correct1 = 0
    incorrect1 = 0
    QN = 0
    correct2 = 0
    incorrect2 = 0
    AL = []
    TeamAns = []
    Teams = []

    def TeamScoreA(self):
        return 'Team A Scores\n--------------------\nCorrect: ' + str(self.correct1) + '\nIncorrect: ' + str(
            self.incorrect1) + '\nTotal: ' + str(self.correct1 - self.incorrect1)

    def TeamScoreB(self):
        return 'Team B Scores\n--------------------\nCorrect: ' + str(self.correct2) + '\nIncorrect: ' + str(
            self.incorrect2) + '\nTotal: ' + str(self.correct2 - self.incorrect2)

    def Skip(self):
        self.play()

    def play(self):
        loc = self.n
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        self.TeamAns = []
        counter = 0
        self.index = math.floor(randint(1, sheet.nrows - 1))
        while self.index in self.AL and counter < 200:
            self.index = math.floor(randint(1, sheet.nrows - 1))
            counter = counter + 1
        if counter < 200:
            print('We are on question ' + str(self.index))
            Category = sheet.cell_value(self.index, 0)
            Type = sheet.cell_value(self.index, 1)
            Format = sheet.cell_value(self.index, 2)
            QuestionA = sheet.cell_value(self.index, 3)
            Answer = sheet.cell_value(self.index, 4)
            AnswerChoices = sheet.cell_value(self.index, 5)
            print(str(Answer))
            self.Q = Question(Category, Type, Format, QuestionA, Answer, AnswerChoices)
            self.AL.append(self.index)
            return self.Q.toStringA()
        else:
            print('Reached File End.')
            self.AL = []
            return self.play()

    def answer(self, A, team):
        if team not in self.Teams:
            self.Teams.append(team)
        if team in self.TeamAns:
            return None
        else:
            self.TeamAns.append(team)
            b = self.Q.checkAsA(A)
            if b:
                return True
            if not b:
                if team is self.Teams[0]:
                    self.incorrect1 = 1 + self.incorrect1
                if team is self.Teams[1]:
                    self.incorrect2 = 1 + self.incorrect2
                    return False
        return False

    def getAnswer(self):
        return self.Q.checkAnwser()

    def FixCheck(self, team):
        if team is self.Teams[0]:
            self.incorrect1 = self.incorrect1 + 1
            self.correct1 = 1 + self.correct1
        if team is self.Teams[1]:
            self.incorrect2 = self.incorrect2 + 1
            self.correct2 = self.correct2 + 1

    def fixScores(self, team):
        if team is self.Teams[0]:
            self.TeamAns = [self.Teams[1]]
        if team is self.Teams[1]:
            self.TeamAns = [self.Teams[0]]

    def changeQuestion(self):
        return False

    def sg(self, role1, role2):
        self.n = 'dataset.xlsx'
        self.AL = []
        self.Teams.append(role1)
        self.Teams.append(role2)
        return self.play()
