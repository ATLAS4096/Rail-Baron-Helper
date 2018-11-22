## Copyright 2018 Corey Ethington
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import time
import random
import Destination_Picker2
import json
import os
from random import randint
from termcolor import colored, cprint

# info
version = 5.10
saveVersion = 4

# Colors:
# sudo pip install termcolor
def _Y(s):
    return colored(s, 'yellow', attrs=['bold'])

def _R(s):
    return colored(s, 'red', attrs=['bold'])

def _G(s):
    return colored(s, 'green', attrs=['bold'])

def _B(s):
    return colored(s, 'blue', attrs=['bold'])

def _C(s):
    return colored(s, 'cyan', attrs=['bold'])

def _I(s):
    return colored(s, 'cyan', attrs=['reverse'])

def _M(s):
    return colored(s, 'yellow', attrs=['reverse'])

# game state variables - To be changed!
allRailroads = False # obsolete

# lists
playerList = [] # contains all player classes - Obsolete, moved to State class
playerDict = {} # correlates a name with a player playerList index - Obsolete, moved to State class

# Game State Class
class State:
    allRailroadsPurchased = False
    playerDict = {}
    playerList = []

    # future-customizable game numbers
    announcePoint = 150 # cash level at which you are required to announce
    declarePoint = 200 # cash level at which you are eligible to win
    startCash = 20 # cash players start with

    saveExt = ".rbs"

    mainLoopTerminate = False
    topLoopTerminate = False

    currentPlayer = 0 # which player's turn it is
    turnCounter = 0 # the number of turns of the game that have elapsed

# Config Class
class Config:
    autoLoad = True
    autoLoadFile = "save3" + State.saveExt
    autoSave = True
    autoSaveFile = "save3" + State.saveExt
    doBackups = True
    developer = True
    corrupted = True
    firstLoad = False

    # update config file from config class
    @classmethod
    def update(self):
        toConfigFile = {}
        toConfigFile["autoLoad"] = Config.autoLoad
        toConfigFile["autoLoadFile"] = Config.autoLoadFile
        toConfigFile["autoSave"] = Config.autoSave
        toConfigFile["autoSaveFile"] = Config.autoSaveFile
        toConfigFile["doBackups"] = Config.doBackups
        toConfigFile["developer"] = Config.developer
        toConfigFile["firstLoad"] = Config.firstLoad

        configFile = open("config.txt", "w+")
        configFile.write(str(toConfigFile))
        configFile.close()

# Player Class
class Player:
    def __init__(self, name):
        self.name = name
    Money = State.startCash
    HomeCity = ""
    Origin = ""
    Destination = ""
    SpeedUpgrade = ""
    aboveAnnouncePoint = False
    aboveDeclarePoint = False
    belowNegativePoint = False

    # adds/subtracts money from the player's balance (negative for subtraction)
    def transact(self, amount):
        self.Money = self.Money + amount

    # checks to see if the destination should become the player's home city.
    def tryHomeCity(self, City):
        if self.HomeCity == "":
            self.HomeCity = City
            print _B(self.name + "'s home city has been set to ") + _G(City)

    # formats variables within class to be saved to file
    def formatForSave(self):
        saveVars = []
        saveVars.append(self.name)
        saveVars.append(self.Money)
        saveVars.append(self.HomeCity)
        saveVars.append(self.Origin)
        saveVars.append(self.Destination)
        saveVars.append(self.SpeedUpgrade)
        return saveVars

    # loads variables formatted for save
    def loadSaveFormat(self, saveVars):
        self.name = saveVars[0]
        self.Money = saveVars[1]
        self.HomeCity = saveVars[2]
        self.Origin = saveVars[3]
        self.Destination = saveVars[4]
        self.SpeedUpgrade = saveVars[5]

    # changes a message point to be above or below
    def passedMessagePoint(self, point):
        if point == "announce":
            if self.aboveAnnouncePoint:
                self.aboveAnnouncePoint = False
            else:
                self.aboveAnnouncePoint = True
        elif point == "declare":
            if self.aboveDeclarePoint:
                self.aboveDeclarePoint = False
            else:
                self.aboveDeclarePoint = True
        elif point == "negative":
            if self.belowNegativePoint:
                self.belowNegativePoint = False
            else:
                self.belowNegativePoint = True

# setup
def newGameSetup():
    playerCount = 0
    try:
        playerCount = int(raw_input(_Y("Number of players: ")))
    except ValueError:
        print _R("Not a number!  Please restart the program!")
        State.topLoopTerminate = True
    i = 0
    betterPlayerList = []
    while i < playerCount:
        iToPrint = i + 1
        playerName = raw_input(_Y("Player " + str(iToPrint) + ": "))
        betterPlayerList.append(Player(playerName))
        State.playerDict[playerName] = i
        i = i + 1
    return betterPlayerList

# calculate the payoff for a given route
def calcPayoff(c1, c2):
    mistake = False
    mainChart = json.loads(open('MainChart.json').read())
    payoff = "empty"
    try:
        payoff = mainChart[c1][c2]
    except KeyError:
        print _R('A city name is invalid.  Please try again.')
        mistake = True

    if payoff == "null":
        tempC1 = c2
        tempC2 = c1
        c1 = tempC1
        c2 = tempC2
        try:
            payoff = mainChart[c1][c2]
        except KeyError:
            print _R('A city name is invalid.  Please try again.')
            mistake = True
    if mistake == False:
        return payoff

# Start of selecting a route for payoff
def newRoute():
    print _M('<----------------Choose a route---------------->')
    city1 = raw_input(_B('Starting City: '))
    city2 = raw_input(_C('Ending City: '))
    return calcPayoff(city1, city2)

# system transfer money between players
def sPay(origin, destination, toPay):
    if State.playerList[origin].Money - toPay >= 0:
        State.playerList[origin].transact(-toPay)
        State.playerList[destination].transact(toPay)
        return True
    else:
        print _R(State.playerList[origin].name + " cannot afford to pay " + str(toPay) + "k!")
        return False

# pays a player for the use of their railroad
def rr(player):
    strTargetPlayer = raw_input(_Y("Player to pay: "))
    targetPlayer = State.playerDict[strTargetPlayer]
    if player == targetPlayer:
        print _R("You cannot pay yourself.")
    else:
        if State.allRailroadsPurchased == False:
            toPay = 5
        else:
            toPay = 10
        paySuccess = sPay(player, targetPlayer, toPay)
        if paySuccess:
            print _G(State.playerList[player].name + " has paid " + State.playerList[targetPlayer].name + " " + str(toPay) + "k to use their railroad")
            print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
            print State.playerList[targetPlayer].name + "'s balance is now " + str(State.playerList[targetPlayer].Money) + "k"

# grants income to a player after they arrive in a city
def payoff(player):
    toPay = newRoute()
    try:
        State.playerList[player].transact(float(toPay))
        print _G(State.playerList[player].name + " recieved " + str(toPay) + "k for their last trip")
        print _R("Please assign yourself a new destination") # TODO: Auto-assign new destination at end of turn.
        print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
    except TypeError:
        nothing = "Don't do anything"

# transfers money to/from players or the bank
def pay(player):
    strTargetPlayer = raw_input(_Y("Player to pay: "))
    if strTargetPlayer == "bank" or strTargetPlayer == "Bank":
        toPay = raw_input(_Y("Amount: "))
        if State.playerList[player].Money - float(toPay) >= 0:
            State.playerList[player].transact(-float(toPay))
            print _G(State.playerList[player].name + " has paid the bank " + toPay + "k")
            print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
        else:
            print _R(State.playerList[player].name + " cannot afford to pay " + str(toPay) + "k!")
    else:
        targetPlayer = State.playerDict[strTargetPlayer]
        if player == targetPlayer:
            print _R("You cannot pay yourself.")
        else:
            toPay = raw_input(_Y("Amount: "))
            paySuccess = sPay(player, targetPlayer, float(toPay))
            if paySuccess:
                print _G(State.playerList[player].name + " has paid " + State.playerList[targetPlayer].name + " " + toPay + "k")
                print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
                print State.playerList[targetPlayer].name + "'s balance is now " + str(State.playerList[targetPlayer].Money) + "k"

# gives a player money from the bank
def income(player):
    amount = raw_input(_Y("Amount: "))
    State.playerList[player].transact(float(amount))
    print _G(State.playerList[player].name + " has recieved " + str(amount) + "k from the bank")
    print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"

# moves to the next player's turn
def nextTurn(player):
    payThousand = True
    usrThousand = raw_input(_Y("Pay thousand (y/n): "))
    if usrThousand == "y":
        State.playerList[player].transact(-1)
        print _G("1k paid to bank.")
        print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
    print _B("End of " + State.playerList[player].name + "'s turn.")
    return "Next Player"

# announces a winner!
def win(player):
    if State.playerList[player].aboveDeclarePoint:
        sure = raw_input(_Y("Are you sure (y/n): "))
        if sure == "y":
            print _M("----------------{" + State.playerList[player].name + " has won the game!}----------------")
            stats(player)
    else:
        print _R("You do not have the " + str(State.declarePoint) + "k needed to win")

# get a player's balance
def bal(player):
    balance = State.playerList[player].Money
    print _G(State.playerList[player].name + "'s balance is " + str(balance) + "k")
    return

def allRR(player):
    sure = raw_input(_Y("Are you sure (y/n): "))
    if sure:
        if State.allRailroadsPurchased == False:
            State.allRailroadsPurchased = True
            print _M("<<---------------{All railroads have been purchased}----------------->>")
            print _B("Royalties to other players are now 10k.")
        else:
            State.allRailroadsPurchased = False
            print _M("<<---------------{All railroads are NO LONGER purchased}----------------->>")
            print _R("You are only allowed to do this if you have modified game rules or are correcting a mistake!  Consult rulebook for more information.")

# help display
commandsHelp = {
    "rr" : "Pay another player for using their railroad",
    "pyf" : "Receive a payoff from travelling between cities",
    "pay" : "Pay another player or the bank.  To pay the bank, specify 'bank'.",
    "in" : "Receive a payment from the bank",
    "n" : "Complete your turn",
    "win" : "Announce you've won the game",
    "bal" : "Check your current balance",
    "allRR" : "Declare that all the railroads have been purchased",
    "help" : "Display this page",
    "lose" : "Declare that you have lost the game",
    "credits" : "Display the credits",
    "k" : "Complete your turn and auto-pay 1k for operating expenses",
    "r" : "Roll the dice",
    "dp" : "Pick a destination",
    "dpm" : "Pick a destination with a manually selected region",
    "home" : "Check your home city",
    "newConfig" : "Overwrite config settings.  Requires confirmation 'configERASE'",
    "homeSet" : "Change your home city",
    "spup" : "Allows you to apply a speed upgrade, such as Express or Super Chief (see rulebook)",
    "speed" : "Check your current speed upgrade, such as Express or Super Chief (see rulebook)",
    "st" : "Display each player's game states.",
    "bn" : "Pay the bank",
    "newGame" : "Start a new game",
    "loadGame" : "Load an existing game",
    "rte" : "View your origin and destination cities",
    "oSet" : "Manually set origin",
    "dSet" : "Manually set destination",
}

# displays all available commands
def helpDisplay(player):
    for keys, values in commandsHelp.items():
        print _B(str(keys)) + ": " +  str(values)

# removes a player from the game - Still broken
def lose(player):
    print _R("This removes the current player from the game.  It cannot be undone.")
    print _R("This function is currently broken and can COMPLETELY RUIN your game.  Type confirmLOSS to continue.")
    password = raw_input(_R("Confirmation keyword: "))
    if password == "confirmLOSS":
        sure = raw_input(_Y("Are you sure (y/n): "))
        if sure:
            del State.playerList[player]
            print _R("Removed " + State.playerList[player].name + " from the game, and also corrupted the playerList file, and therefore your save file!  Have fun! >:)")
    else:
        print _B("Canceled")

# display the credits
def cds(player):
    print _B("Created by Corey Ethington.")

def k(player):
    State.playerList[player].transact(-1)
    print _G("1k paid to bank.")
    print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
    print _B("End of " + State.playerList[player].name + "'s turn.")
    return "Next Player"

def r(player):
    roll1 = randint(1, 6)
    roll2 = randint(1, 6)
    roll3 = 0
    if roll1 + roll2 == 12 or State.playerList[player].SpeedUpgrade == "Express" and roll1 == roll2 or State.playerList[player].SpeedUpgrade == "Super Chief":
        roll3 = randint(1, 6)
        if State.playerList[player].SpeedUpgrade != "":
            print _B(State.playerList[player].name + " has " + State.playerList[player].SpeedUpgrade)
    diceRoll = roll1 + roll2 + roll3
    if roll3 == 0:
        print "Rolled " + _B(str(roll1)) + " and " + _B(str(roll2))
    else:
        print "Rolled " + _B(str(roll1)) + ", " + _B(str(roll2)) + ", and " + _B(str(roll3))
    print _G(diceRoll)

# gets a randomly selected destination, using the Destination Picker file.
def dp(player):
    tryCity = Destination_Picker2.getCity()
    State.playerList[player].tryHomeCity(tryCity)
    State.playerList[player].Origin = State.playerList[player].Destination
    State.playerList[player].Destination = tryCity

# lets the user pick the region for their randomly selected destination, using the Destination Picker file.
def dpm(player):
    tryCity = Destination_Picker2.chooseRegion()
    if tryCity != _R("--ERROR--"):
        State.playerList[player].tryHomeCity(tryCity)
        State.playerList[player].Origin = State.playerList[player].Destination
        State.playerList[player].Destination = tryCity

# lets the player set or change their home city manually
def homeSet(player):
    determineHome = raw_input(_Y("New home city: "))
    State.playerList[player].HomeCity = determineHome
    print _B(State.playerList[player].name + "'s home city has been set to ") + _G(determineHome)

# checks the player's home city
def home(player):
    if State.playerList[player].HomeCity != "":
        print _B(State.playerList[player].name + "'s home city is " + State.playerList[player].HomeCity)
    else:
        print _R(State.playerList[player].name + " does not have a home city yet.  Try homeSet to add a home city.")

# configure your speed upgrades, E.G. Express, Super Chief
def speedUp(player):
    currentUpgrade = State.playerList[player].SpeedUpgrade
    if currentUpgrade == "":
        print _B(State.playerList[player].name + " currently has no speed upgrade.")
    else:
        print _B(State.playerList[player].name + " currently has the " + State.playerList[player].SpeedUpgrade)
    newUpgrade = raw_input(_Y("New upgrade (<enter> with no text to return to no upgrade): "))
    State.playerList[player].SpeedUpgrade = newUpgrade
    if newUpgrade == "":
        print _B(State.playerList[player].name + " no longer has any speed upgrades.")
    else:
        print _B(State.playerList[player].name + " now has the " + newUpgrade)

# check your speed upgrade
def speed(player):
    currentUpgrade = State.playerList[player].SpeedUpgrade
    if currentUpgrade == "":
        print _B(State.playerList[player].name + " currently has no speed upgrade.")
    else:
        print _B(State.playerList[player].name + " currently has the " + State.playerList[player].SpeedUpgrade)

# create a new config file with the default settings
def newConfig(player):
    print _R("About to erase config file!  Enter correct confirmation to continue.  Type 'help' for confirmation keyword.")
    password = raw_input(_R("Confirmation keyword: "))
    if password == "configERASE":
        sure = raw_input(_R("Do not attempt this unless you are a developer.  Are you really sure (y/n): "))
        if sure == "y":
            f = open("config.txt", "w+")
            toConfig = {}
            toConfig["autoLoad"] = True # Auto-loads a save file on startup
            toConfig["autoLoadFile"] = "save2" + State.saveExt # target file for autoLoad
            toConfig["autoSave"] = True # Auto-saves the running game to a file
            toConfig["autoSaveFile"] = "save2" + State.saveExt # target file for autosave.  Can be same as autoLoad target
            toConfig["doBackups"] = True # backs up the save file before autoLoading
            toConfig["developer"] = True # indicates developer mode.  Doesn't affect anything else yet
            toConfig["firstLoad"] = False
            f.write(str(toConfig))
            f.close()

# create a new config file without asking
def newAutoConfig():
    file = open("config.txt", "w+")
    toConfig = {}
    toConfig["autoLoad"] = True  # Auto-loads a save file on startup
    toConfig["autoLoadFile"] = "save2" + State.saveExt  # target file for autoLoad
    toConfig["autoSave"] = True  # Auto-saves the running game to a file
    toConfig["autoSaveFile"] = "save2" + State.saveExt  # target file for autosave.  Can be same as autoLoad target
    toConfig["doBackups"] = True  # backs up the save file before autoLoading
    toConfig["developer"] = True  # indicates developer mode.  Doesn't affect anything else yet
    toConfig["firstLoad"] = False
    file.write(str(toConfig))
    file.close()

# display all player's stats
def stats(player):
    p = 0
    print _B(">>>--------Statistics--------<<<")
    while p < len(State.playerList):
        print _G(">------" + State.playerList[p].name + "------<")
        print _B("Balance: ") + str(State.playerList[p].Money)
        if State.playerList[p].SpeedUpgrade != "":
            print _B("Speed Upgrade: ") + State.playerList[p].SpeedUpgrade
        else:
            print _B("Speed Upgrade: ") + "None"

        p = p + 1

# pay the bank directly
def bn(player):
    toPay = raw_input(_Y("Amount: "))
    if State.playerList[player].Money - float(toPay) >= 0:
        State.playerList[player].transact(-float(toPay))
        print _G(State.playerList[player].name + " has paid the bank " + toPay + "k")
        print State.playerList[player].name + "'s balance is now " + str(State.playerList[player].Money) + "k"
    else:
        print _R(State.playerList[player].name + " cannot afford to pay " + str(toPay) + "k!")

def newGame(player):
    print _R("This will abandon your current game and start a new one.  ") + _B("Your progress will be saved.")
    sure = raw_input(_Y("Are you sure (y/n): "))
    if sure == "y":
        newFileName = raw_input(_Y("New Game name: "))
        Config.autoLoadFile = newFileName + State.saveExt
        Config.autoSaveFile = newFileName + State.saveExt
        Config.firstLoad = True

        Config.update()

        State.mainLoopTerminate = True

def loadGame(player):
    print _R("This will abandon your current game and load an existing one.  ") + _B("Your progress will be saved.")
    sure = raw_input(_Y("Are you sure (y/n): "))
    if sure == "y":
        newFileName = raw_input(_Y("Save name: ")) + State.saveExt
        try:
            test = open(os.path.join("./Saves", newFileName), "r")
            if str(test) != "":
                Config.autoLoadFile = newFileName
                Config.autoSaveFile = newFileName
                Config.firstLoad = False

                Config.update()

                State.mainLoopTerminate = True
        except IOError:
            print _R("File does not exist.")

# print the player's origin and destination cities
def rte(player):
    print _B("Origin: ") + State.playerList[player].Origin
    print _B("Destination: ") + State.playerList[player].Destination
    print _G("Payoff: ") + str(calcPayoff(State.playerList[player].Origin, State.playerList[player].Destination))

# manually set origin
def oSet(player):
    newOri = raw_input(_Y("New origin: "))
    State.playerList[player].Origin = newOri
    print _G("Your origin city is now " + State.playerList[player].Origin)

# manually set destination
def dSet(player):
    newDest = raw_input(_Y("New destination: "))
    State.playerList[player].Destination = newDest
    print _G("Your destination city is now " + State.playerList[player].Destination)

# commands
commandsDict = {
    "rr" : rr,
    "pyf" : payoff,
    "pay" : pay,
    "in" : income,
    "n" : nextTurn,
    "win" : win,
    "bal" : bal,
    "allRR" : allRR,
    "help" : helpDisplay,
    "lose" : lose,
    "credits" : cds,
    "k" : k,
    "r" : r,
    "dp" : dp,
    "dpm" : dpm,
    "homeSet" : homeSet,
    "newConfig" : newConfig,
    "home" : home,
    "spup" : speedUp,
    "speed" : speed,
    "st" : stats,
    "bn" : bn,
    "newGame" : newGame,
    "loadGame" : loadGame,
    "rte" : rte,
    "oSet" : oSet,
    "dSet" : dSet,
}

# check for events
def eventChecker():
    p = 0
    while p < len(State.playerList):
        if State.playerList[p].Money >= State.announcePoint and not State.playerList[p].aboveAnnouncePoint:
            State.playerList[p].passedMessagePoint("announce")
            print _M("<<---------------{" + State.playerList[p].name + " now has above " + str(State.announcePoint) + "k!}----------------->>")
        if State.playerList[p].Money < State.announcePoint and State.playerList[p].aboveAnnouncePoint:
            State.playerList[p].passedMessagePoint("announce")
            print _M("<<---------------{" + State.playerList[p].name + " NO LONGER now has above " + str(State.announcePoint) + "k!}----------------->>")

        if State.playerList[p].Money >= State.declarePoint and not State.playerList[p].aboveDeclarePoint:
            State.playerList[p].passedMessagePoint("declare")
            print _M("<<---------------{" + State.playerList[p].name + " now has above " + str(State.declarePoint) + "k and is eligible to Declare and win!}----------------->>")
        if State.playerList[p].Money < State.declarePoint and State.playerList[p].aboveDeclarePoint:
            State.playerList[p].passedMessagePoint("declare")
            print _M("<<---------------{" + State.playerList[p].name + " NO LONGER now has above " + str(State.declarePoint) + "k and is NO LONGER eligible to Declare and win!}----------------->>")

        if State.playerList[p].Money < 0 and not State.playerList[p].belowNegativePoint:
            State.playerList[p].passedMessagePoint("negative")
            print _M("<<---------------{" + State.playerList[p].name + " now in debt!  They must sell railroads on this turn or lose the game!}----------------->>")
        if State.playerList[p].Money >= 0 and State.playerList[p].belowNegativePoint:
            State.playerList[p].passedMessagePoint("negative")
            print _M("<<---------------{" + State.playerList[p].name + " NO LONGER in debt!  They are not in danger of losing.}----------------->>")

        p = p + 1

# saves the game state to a file
def saveToFile(fileName):
    data = []
    #data.append(playerList)
    playersData = []
    p = 0
    while p < len(State.playerList):
        playersData.append(State.playerList[p].formatForSave())
        #print playerList[p].formatForSave()
        p = p + 1
    data.append(playersData)
    data.append(State.playerDict)
    data.append(saveVersion)
    data.append(State.currentPlayer)
    data.append(State.turnCounter)
    file = open(os.path.join("./Saves", fileName), "w")
    file.write(str(data))
    file.close()

def commandInterpreter(allRailroadsC):
    newTurn = True
    commandReturn = ""
    while not State.mainLoopTerminate:
        eventChecker()
        if newTurn:
            print _I("<----------------" + State.playerList[State.currentPlayer].name + "'s turn---------------->")
            newTurn = False
        command = raw_input("> ")
        try:
            commandReturn = commandsDict[command](State.currentPlayer)
        except KeyError:
            print _R('Invalid Command.  Try "help"')
        except ValueError:
            print _R('Not a number!')

        if Config.autoSave:
            saveToFile(Config.autoSaveFile)

        # TODO: Maybe migrate to classes and event listener, bypassing the weird command return thing?
        if commandReturn == "Next Player":
            if State.currentPlayer + 1 < len(State.playerList):
                State.currentPlayer = State.currentPlayer + 1
            else:
                State.currentPlayer = 0
                State.turnCounter = State.turnCounter + 1
                print _B("<----------------Turn " + str(State.turnCounter) + "---------------->")
            newTurn = True

        if Config.autoSave:
            saveToFile(Config.autoSaveFile)

# creates a new file - Obsolete!  May be reincarnated in a reimplementation!
def createSaveFile():
    name = ""
    createSave = raw_input(_Y("Create a save file for this game (y/n): "))
    if createSave == "y":
        name = raw_input(_Y("Save file name: "))
        f = open(os.path.join("./Saves", name + State.saveExt), "w+")
        print _B("Successfully created save file")
    return name

# auto-creates a new file? - Obsolete!  May be reincarnated in a reimplementation!
def autoCreateSaveFile(fileName):
    f = open(os.path.join("./Saves", fileName), "w+")
    print _B("Successfully created save file")
    return fileName

# loads config file
def loadConfig():
    f = file
    try:
        f = open("config.txt")
        print _B('Loaded config file "config.txt"')
    except IOError:
        print _R("The config.txt file is missing!  A new one with the default settings has been created.")
        newAutoConfig()
    configFileData = {}
    try:
        configFileData = eval(f.read())
        Config.corrupted = False
    except SyntaxError:
        print _R("ERROR >>> Failed to load config file.")
        Config.corrupted = True
    return configFileData

# reads config file
def readConfig(configData):
    Config.doBackups = configData["doBackups"]
    if not Config.doBackups:
        print _R("Backups are currently disabled.")

    Config.autoSave = configData["autoSave"]
    Config.autoSaveFile = configData["autoSaveFile"]

    Config.developer = configData["developer"]

    Config.firstLoad = configData["firstLoad"]

    if configData["autoLoad"] == True:
        Config.autoLoadFile = configData["autoLoadFile"]
        if Config.doBackups:
            print _B(backup(Config.autoLoadFile))
        Config.autoLoad = True
    else:
        Config.autoLoad = False

# backup the currently loaded file to backup.rbs
def backup(origin):
    if not Config.firstLoad:
        try:
            originFile = open(os.path.join("./Saves", origin))
            fromOrigin = originFile.read()
            destinationFile = open(os.path.join("./Saves", "backup" + State.saveExt), "w+")
            destinationFile.write(str(fromOrigin))
            return "Backup Successful"
        except IOError:
            print _R("Backup failed.  File missing.")
            return ""

# load raw data from a save
def loadSave(auto):
    if auto:
        fileName = Config.autoLoadFile
    else:
        fileName = (raw_input(_Y("File to load: ")) + State.saveExt)
    saveFile = open(os.path.join("./Saves", fileName))
    try:
        saveData = eval(saveFile.read())
        if saveData[2] != saveVersion:
            print _R("Save file is wrong version, and will not load!")
            print _B("Expected save version is " + str(saveVersion))
            if saveData[2] > 3:
                print _R("Save version from file: ") + str(saveData[2])
            else:
                print _R("Save version is older than Version 3.")
            return False
        elif saveData[2] == 4:
            return saveData
    except SyntaxError:
        print _R("Save file " + fileName + "is corrupted!")
        return False

# decode data from a save
def decodeSave(data, fileName):
    p = 0
    localPlayerDict = data[1]
    while p < len(data[0]):
        State.playerList.append(Player("initName"))
        State.playerList[p].loadSaveFormat(data[0][p])
        p = p + 1
    State.currentPlayer = data[3]
    State.turnCounter = data[4]
    print _B("Successfully loaded save file " + fileName)
    State.playerDict = localPlayerDict

# start up the program, load stuff, get user inputs, etc.
def initialize():
    print _B("Rail Baron Helper, version " + str(version))

    rawConfigData = loadConfig()
    if not Config.corrupted:
        readConfig(rawConfigData)

    saveWorking = False
    if Config.autoLoad and not Config.firstLoad:
        try:
            saveFile = open(os.path.join("./Saves", Config.autoLoadFile))
            print "Got this far..."
            saveData = loadSave(saveFile)
            saveWorking = True
            if saveData == False:
                saveWorking = False
            else:
                decodeSave(saveData, Config.autoLoadFile)
        except IOError:
            saveWorking = False
            print _R("Failed to load save file.  File may be missing.")
        if not saveWorking:
            State.playerList = newGameSetup()
    else:
        State.playerList = newGameSetup()

    Config.firstLoad = False
    Config.update()

# Start of program
if __name__ == '__main__':
    #State.topLoopTerminate = False
    END = False
    while not State.topLoopTerminate:
        initialize()
        State.mainLoopTerminate = False
        while not State.mainLoopTerminate:
            try:
                allRailroads = commandInterpreter(allRailroads) #filename2
            except KeyboardInterrupt:
                print ""
                State.mainLoopTerminate = True
                State.topLoopTerminate = True

# TODO: Save turn number to save file.  Will require updating save version to 4.
