#!/usr/bin/env python3.4
# Created by Tomasz Błahut @ 2017
# v1.2

import random

#---Helpers---#

figureMap = {"2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "10" : 10, "J" : 10, "Q" : 10, "K" : 10, "AS" : 1}

colorList = ["H", "D", "C", "S"]

#---Card Class START---#

class Card(object):
	def __init__(self, color, figure):
		self.color = color
		self.figure = figure
		self.special = True if figure == "AS" else False
		self.value = figureMap[figure]
	def print(self):
		pass #TODO

#---Card Class END---#

#---Deck Class START---#

class Deck(object):
	def __init__(self):
		self.cards = set()
		self.players = []
		self.nonPlayers = []
		self.inGame = True
		for color in colorList:
			for figure in figureMap.keys():
				self.cards.add(Card(color, figure))

	def drawCard(self, hand):
		if(len(self.cards) < 1):
			print("No more cards!")
			return None
		if(hand.isFinished()):			
			print("Player has ended his game!")
			return None
		card = random.sample(self.cards, 1)[0]
		self.cards.remove(card)
		hand.addCard(card)

	def registerPlayer(self, hand, ai = False):
		if(ai):
			self.croupier = hand
		else:
			if hand not in self.players:
				self.players.append(hand)

	def nextTurn(self):
		i = 0
		while True:
			userAnswer = input(self.players[i].name + " has {0} points: ".format(self.players[i].getPoints()))
			if(userAnswer != 's'):
				self.drawCard(self.players[i])
			else:
				self.players[i].end()
			if(self.players[i].isFinished()):
				self.nonPlayers.append(self.players[i])
				del self.players[i]
				if(len(self.players) == 0):
					break
				i = i % len(self.players)
			else:
				i = (i + 1) % len(self.players)
			yield

	def startGame(self):
		while self.croupier.getPointsInt() < 17:
			self.drawCard(self.croupier)
		for player in self.players * 2:
			self.drawCard(player)

	def printWinner(self):
		winner = [self.croupier]
		for player in self.nonPlayers:
			if(player.getPointsInt() > 21):
				continue
			else:
				if(player.getPointsInt() > winner[0].getPointsInt() or winner[0].getPointsInt() > 21):
					winner = [player]
				elif(player.getPointsInt() == winner[0].getPointsInt()):
					winner.append(player)
		print("******")
		if(len(winner) > 1):
			print("Winners({0}): ".format(len(winner)), end = '')
			for player in winner:
				print(player.name, end = ' ')
			print('')
		else:
			if(winner[0].getPointsInt() <= 21):
				print("Winner: ", winner[0].name)
			else:
				print("There is no winner")
		print('')
		
		print("AI: ", self.croupier.getPointsInt())
		for player in self.nonPlayers:
			print(player.name, ": ", player.getPointsInt())
		print("******")

#---Deck Class END---#

#---Hand Class START---#

class Hand(object):
	def __init__(self, name = "Player"):
		self.cards = []
		self.points = 0
		self.special = False
		self.finished = False
		self.name = name

	def addCard(self, card):
		self.cards.append(card)
		self.points += card.value
		if(card.special):
			self.special = True

		return self.check()

	def check(self):
		if(self.points >= 21 or (self.special and self.points == 11)):
			self.end()
			return True
		else:
			return False

	def getPoints(self):
		if(self.special and (self.points + 10 <= 21)):
			return str("{0}/({1})".format(self.points, self.points + 10))
		else:
			return str(self.points)

	def getPointsInt(self):
		if(self.special and (self.points + 10 <= 21)):
			return self.points + 10
		else:
			return self.points

	def split(self):
		pass #TODO

	def end(self):
		self.finished = True

	def isFinished(self):
		return self.finished

#---Hand Class END---#

#---Main Loop START---#

game = Deck()

game.registerPlayer(Hand("AI"), True)

while True:
	name = input("Type name of the player: ")
	if(name != ''):
		game.registerPlayer(Hand(name))
	else:
		if(len(game.players) != 0):
			break

game.startGame()

gameRound = game.nextTurn()

while True:
	try:
		next(gameRound)
	except (StopIteration):
		break

game.printWinner()

#---Main Loop END---#
