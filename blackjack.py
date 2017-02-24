#!/usr/bin/env python3.4
# Created by Tomasz Błahut @ 2017
# v1.3

import random
import socket
import sys

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
			message = "You have {0} points: ".format(self.players[i].getPoints())

			if self.players[i].tcpHandle == None:
				userAnswer = input(message)
			else:
				userAnswer = Lan.sendAndRequestData(self.players[i].tcpHandle[0], message)
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
		message = "******\n"
		if(len(winner) > 1):
			message += "Winners({0}): ".format(len(winner))
			for player in winner:
				message += player.name
			message += '\n'
		else:
			if(winner[0].getPointsInt() <= 21):
				message += "Winner: " + winner[0].name + "\n"
			else:
				message += "There is no winner\n"
		message += '\n'
		
		message += "AI: " + str(self.croupier.getPointsInt()) + "\n"
		for player in self.nonPlayers:
			if player.tcpHandle == None:				
				message += player.name + "(host): " + str(player.getPointsInt()) + "\n"
			else:
				message += player.name + "(" + str(player.tcpHandle[1][0]) + "): " + str(player.getPointsInt()) + "\n"
		message += "******\n"

		for player in self.nonPlayers:
			if player.tcpHandle == None:
				print(message)
			else:
				Lan.sendData(player.tcpHandle[0], message + "#gameEnd")
				player.tcpHandle[0].close()

#---Deck Class END---#

#---Hand Class START---#

class Hand(object):
	def __init__(self, tcpHandle, name = "Player"):
		self.cards = []
		self.points = 0
		self.special = False
		self.finished = False
		self.name = name
		self.tcpHandle = tcpHandle

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

#---Lan Class START---#

class Lan:
	def sendData(connection, data):
		connection.sendall("#start#{}#end".format(data).encode("ASCII"))

	def requestData(connection):
		data = ''
		while True:
			buf = connection.recv(16)
			data += buf.decode("ASCII")
			if "#end" in data:
				break
			elif "#start#" in data:
				data = data.replace("#start#", "")
			elif buf:
				pass
			else:
				break

		return data.replace("#start#", "").replace("#end", "")

	def sendAndRequestData(connection, data):
		Lan.sendData(connection, data)
		return Lan.requestData(connection)
	
#---Lan Class END---#

#---Setting up a server---#

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv) < 2:
	serverAddress = ('', 6789)
	sock.bind(serverAddress)

	print("Starting up on", (sock.getsockname()))

	sock.listen(1)

	game = Deck()

	game.registerPlayer(Hand(None,"AI"), True)

	name = input("Type your name: ")
	if(name != ''):
		game.registerPlayer(Hand(None,name))
	else:
		game.registerPlayer(Hand(None))

	try:
		print("Waiting for players (press CTRL-C to start game)")
		while True:
			connectionTuple = sock.accept()
			connection, clientAddress = connectionTuple
			print("Connected: {0}".format(clientAddress))
			data = Lan.requestData(connection)
			game.registerPlayer(Hand(connectionTuple, data))
			print("Player {} ({}) joined".format(data, clientAddress[0]))
	except KeyboardInterrupt:
		print("\nStarting game...")

	game.startGame()

	gameRound = game.nextTurn()

	while True:
		try:
			next(gameRound)
		except (StopIteration):
			break

	game.printWinner()

else:
	serverAddress = (sys.argv[1], 6789)
	sock.connect(serverAddress)

	name = input("Type your name: ")
	Lan.sendData(sock, name)
	
	while True:
		data = Lan.requestData(sock)
		if "#gameEnd" in data:
			print(data.split("#gameEnd")[0])
			break

		message = input(data)
		Lan.sendData(sock, message)

#---Main Loop START---#

while False:
	name = input("Type name of the player: ")
	if(name != ''):
		game.registerPlayer(Hand(name))
	else:
		if(len(game.players) != 0):
			break

sock.close()

#---Main Loop END---#
