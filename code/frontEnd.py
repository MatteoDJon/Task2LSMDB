from middleLayer import middleLayer
import pymongo
from datetime import datetime
from getpass import getpass
from pprint import pprint
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class frontEnd:
  
    def __init__(self):
       
        self.firstLevelCommands=["!browseNations","!findHotel","!findReviewer","!reccomendedHotelForReviewer","!deleteHotel","!deleteReviewer","!deleteReview","!commands","!login","!logout","!quit"]
        self.firstLevelDescriptions=[": read all the nation",": search an hotel and read its informations",": search a reviewer and read its information",": read the suggested hotel for a reviewer",": delete an hotel",": delete a reviewer",": delete the review whose number is in the list of the reviews you've read",": read all the commands",": login in with your credentials","",": exit from the application"]
        self.secondLevelDescription=[ ": show the statistics of a nation of the list",": show the analytics of a nation of the list",": read the cities of a nation",": show the most popular hotels of the nation",": show the most popular reviewers of the nation",": show a list of possible fake reviewers",": delete a nation(only if you're an admin)",": read all the commands",": login in with your credentials","",": return to the main level",": exit from the application"]  
        self.secondLevelCommands=["!showStatistics","!showAnalytics","!browseCities","!popularHotels","!popularReviewers","!fakeReviewers","!delete","!commands","!login","!logout","!back","!quit"] 
        self.thirdLevelCommands=["!showStatistics","!showAnalytics","!popularHotels","!popularReviewers","!delete","!commands","!login","!logout","!back","!quit"]
        self.thirdLevelDescription=[ ": show the statistics of a city of the list",": show the analytics of a city of the list",": show the most popular hotels of the city",": show the most popular reviewers of the nation",": delete a city(only if you're an admin)",": read all the commands",": login in with your credentials","",": return to the nation level",": exit from the application"]       
        self.typeUser="generic"
        self.level="first"
        self.middleLayer=middleLayer()
    
    def showCommands(self):
        commands=[]
        descriptions=[]
        if(self.level=="first"):
            commands=self.firstLevelCommands
            descriptions=self.firstLevelDescriptions
        elif(self.level=="second"):
            commands=self.secondLevelCommands
            descriptions=self.secondLevelDescription
        else:
            commands=self.thirdLevelCommands
            descriptions=self.thirdLevelDescription
        numberOption=len(commands)
        index=0;
        while index<numberOption:
            if(("!delete" in commands[index])==True and self.typeUser=="admin" or ("!delete" in commands[index])==False):
                print(commands[index] + descriptions[index] +  "\n")
            else:
                pass
            index+=1
            
    def executeFirstLevelCommand(self):
        commandType=input("Command choice:")
        if(commandType==self.firstLevelCommands[0]):
            self.middleLayer.showNations()
            self.level="second"
            self.showCommands()
            return self.executeSecondLevelCommand()
        elif(commandType==self.firstLevelCommands[1]):
            self.hotelName=input("Please, insert a name of the hotel you're interested in: ")
            self.middleLayer.showHotel(self.hotelName)
            return True
        elif(commandType==self.firstLevelCommands[2]):
            reviewerName=input("Insert Reviewer Name:")
            nations=self.middleLayer.listOfNationsFromReviewer(reviewerName)
            for nation in nations:
                reviewList=self.middleLayer.showReviewsOfReviewer(nation,reviewerName)
            return True
        elif(commandType==self.firstLevelCommands[3]):
            reviewerName=input("Insert Reviewer Name:")
            self.middleLayer.showReccomendedHotel(reviewerName)
            return True
        elif(commandType==self.firstLevelCommands[4]):
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            informations=input("Insert  Nation and Hotel Name separated from , : ")
            splittedInput=informations.split(',')
            if(len(splittedInput)<2):
                print("Missing some informations!"+"\n")
            else:
                if(self.middleLayer.deleteHotel(splittedInput[0],splittedInput[1])==True):
                    self.middleLayer.deleteOnGraphDB("Hotel",splittedInput[1],"")
                    print("Successfull delete!"+"\n")
                else:
                    print("Unable to delete!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[5]):
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            reviewerName=input("Insert Reviewer Name:")
            self.middleLayer.deleteReviewer(reviewerName)
            self.middleLayer.deleteOnGraphDB("Reviewer",reviewerName,"")
            return True
        elif(commandType==self.firstLevelCommands[6]):
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            inputString=input("Insert reviewer, nation and review number:")
            self.middleLayer.deleteReview(inputString)
            return True
        elif(commandType==self.firstLevelCommands[7]):
            self.showCommands()
            return True
        elif(commandType==self.firstLevelCommands[8]):
            credentials=input("Insert User and Password separated from a ,"+"\n")
            splittedCredentials=credentials.split(',')
            if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                self.typeUser="admin"
                self.middleLayer.callSwitchConnection("generic")
                print("Login successfull")
            else:
                print("Login failed or yet done!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[9]):
            if(self.typeUser=="admin"):
                self.typeUser="generic"
                self.middleLayer.callSwitchConnection("admin")
                print("Logout successfull!"+"\n")
            else:
                print("You're not logged in!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[10]):
            print("The application is closing!")
            self.middleLayer.closeConnection()
            return False
        else:
            print("Unknown command,try again!")
            return True

    def executeSecondLevelCommand(self):
        continueWhile=True
        continueApplication=True
        while(continueWhile):
            commandType=input("Command choice: ")         
            if(commandType==self.secondLevelCommands[0]):
                nationName=input("Insert the name of the nation: ")
                if(self.middleLayer.presence("Nation",nationName,"")==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showNationStatistics(nationName)
            elif(commandType==self.secondLevelCommands[1]):
                nationName=input("Insert the name of the nation: ")
                if(self.middleLayer.presence("Nation",nationName,"")==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showNationAnalytics(nationName)
            elif(commandType==self.secondLevelCommands[2]):
                nationName=input("Insert the name of the nation: ")
                if(self.middleLayer.presence("Nation",nationName,"")==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCities(nationName)
                    self.level="third"
                    self.showCommands()
                    continueWhile=self.executeThirdLevelCommand(nationName)
                    if(continueWhile==False):
                        continueApplication=False
            elif(commandType==self.secondLevelCommands[3]):
                nationName=input("Insert the name of the nation: ")
                parameters=[]
                parameters.append(nationName)
                self.middleLayer.showPopularHotel("Nation",parameters)
            elif(commandType==self.secondLevelCommands[4]):
                nationName=input("Insert the name of the nation: ")
                parameters=[]
                parameters.append(nationName)
                self.middleLayer.showPopularReviewer("Nation",parameters)
            elif(commandType==self.secondLevelCommands[5]):
                nationName=input("Insert the name of the nation: ")
                self.middleLayer.showFakeReviewer(nationName)
            elif(commandType==self.secondLevelCommands[6]):
                if(self.typeUser=="generic"):
                    print("You don't have the credentials to do this operation!"+"\n")
                else:
                    nationName=input("Insert the name of the nation: ")
                    self.middleLayer.deleteNation(nationName)
                    self.middleLayer.deleteOnGraphDB("Nation",nationName,"")
            elif(commandType==self.secondLevelCommands[7]):
                self.showCommands()
            elif(commandType==self.secondLevelCommands[8]):
                credentials=input("Insert User and Password separated from a ,"+"\n")
                splittedCredentials=credentials.split(',')
                if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                    self.typeUser="admin"
                    self.middleLayer.callSwitchConnection("generic")
                    print("Login successfull")
                else:
                    print("Login failed or yet done!"+"\n")
            elif(commandType==self.secondLevelCommands[9]):
                if(self.typeUser=="admin"):
                    self.typeUser="generic"
                    self.middleLayer.callSwitchConnection("admin")
                    print("Logout successfull!"+"\n")
                else:
                    print("You're not logged in!"+"\n")
            elif(commandType==self.secondLevelCommands[10]):
                self.level="first"
                print("Back to precedent level"+"\n")
                continueWhile=False
                continueApplication=True
            elif(commandType==self.secondLevelCommands[11]):
                print("The application is closing!"+"\n")
                self.middleLayer.closeConnection()
                continueWhile=False
                continueApplication=False
            else:
                print("Unknown command,try again!"+"\n")
        return continueApplication
		
    def executeThirdLevelCommand(self,nation):
        self.middleLayer.printLine()
        continueWhile=True
        continueApplication=True
        while(continueWhile):
            commandType=input("Command choice: ")
            if(commandType==self.thirdLevelCommands[0]):
                cityName=input("Insert the name of the city: ")
                if(self.middleLayer.presence("city",nation,cityName)==False):
                    print("City unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCityStatistics(nation,cityName)
            elif(commandType==self.thirdLevelCommands[1]):
                cityName=input("Insert the name of the city: ")
                if(self.middleLayer.presence("city",nation,cityName)==False):
                    print("City unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCityAnalytics(nation,cityName)
            elif(commandType==self.thirdLevelCommands[2]):
                cityName=input("Insert the name of the city: ")
                parameters=[]
                parameters.append(nation)
                parameters.append(cityName)
                self.middleLayer.showPopularHotel("City",parameters)
            elif(commandType==self.thirdLevelCommands[3]):
                cityName=input("Insert the name of the city: ")
                parameters=[]
                parameters.append(nation)
                parameters.append(cityName)
                self.middleLayer.showPopularReviewer("City",parameters)   
            elif(commandType==self.thirdLevelCommands[4]):
                cityName=input("Insert the name of the city: ")
                if(self.typeUser=="generic"):
                    print("You don't have the credentials to do this operation!"+"\n")
                else:
                    self.middleLayer.deleteCity(nation,cityName)
                    self.middleLayer.deleteOnGraphDB("City",cityName,"")
            elif(commandType==self.thirdLevelCommands[5]):
                self.showCommands()
            elif(commandType==self.thirdLevelCommands[6]):
                credentials=input("Insert User and Password separated from a ,"+"\n")
                splittedCredentials=credentials.split(',')
                if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                    self.typeUser="admin"
                    self.middleLayer.callSwitchConnection("generic")
                    print("Login successfull")
                else:
                    print("Login failed or yet done!"+"\n")
            elif(commandType==self.thirdLevelCommands[7]):
                if(self.typeUser=="admin"):
                    self.typeUser="generic"
                    self.middleLayer.callSwitchConnection("admin")
                    print("Logout successfull!"+"\n")
                else:
                    print("You're not logged in!"+"\n")
            elif(commandType==self.thirdLevelCommands[8]):
                print("Back to precedent level"+"\n")
                self.level="second"
                continueWhile=False
                continueApplication=True
            elif(commandType==self.thirdLevelCommands[9]):
                print("The application is closing!"+"\n")
                self.middleLayer.closeConnection()
                continueWhile=False
                continueApplication=False
            else:
                print("Unknown command,try again!"+"\n")
        return continueApplication
        