import pymongo
from datetime import datetime
from getpass import getpass
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class Connect:

    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db=self.myclient["tripbooking"]
        
    def close(self):
        if self.myclient != "":
            self.myclient.close()
    
    def deleteCityFromDB(self,nation,city):
        return self.db.Hotel.delete_many({"nation":nation,"city":city})
    
    def deleteHotelFromDB(self,nation,hotel):
        return self.db.Hotel.delete_one({"nation":nation,"name":hotel})
    
    def deleteNationFromDB(self,entityName):
        self.db.Hotel.delete_many({"nation":entityName})
        self.db.Nation.delete_one({"name":entityName})
            
    def deleteReviewerOnNationFromDB(self,nationName,reviewerName):
        #self.db.Hotel.update_many({"nation":nationName},{"$pull":{"reviewList":{"reviewer":reviewerName}}})
        self.db.Nation.update_one({"name":nationName},{"$pull":{"reviewers":reviewerName}})
    
    def deleteReviewOnHotelFromDB(self,nationName,hotelName,reviewer,month,year,text):
        return self.db.Hotel.update_one({"nation":nationName,"name":hotelName},{"$pull":{"reviewList":{"reviewer":reviewer,"month":month,"year":year,"text":text}}})
    
    def find_hotel(self,hotelName):
        return self.db.Hotel.find_one({"name":hotelName})
    
    def find_nations(self):
        return self.db.Nation.find({},{"name":1,"_id":0})
    
    def find_citiesWithCount(self,nationName):
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName}},{"$group":{"_id":"$city","count":{"$sum":1}}}])
   
    def getCommentedHotel(self,nationName,reviewerName):
        return self.connection.Hotel.find({"nation":nationName,"reviewList.reviewer":reviewerName},{"_id":0,"name":1})
   
    def getCityAnalytics(self,nation,city):
        return self.db.Hotel.aggregate([{"$match":{"nation":nation,"city":city,"position":{"$ne":0.0},"cleanliness":{"$ne":0.0},"service":{"$ne":0.0},"qualityPrice":{"$ne":0.0}}},{"$group":{"_id":"null","averagePosition":{"$avg":"$position"},"averageCleanliness":{"$avg":"$cleanliness"},"averageService":{"$avg":"$service"},"averageQualityPrice":{"$avg":"$qualityPrice"}}},{"$project":{"_id":"!null","pool":[{"name":"averagePosition","value":"$averagePosition"},{"name":"averageCleanliness","value":"$averageCleanliness"},{"name":"averageService","value":"$averageService"},{"name":"averageQualityPrice","value":"$averageQualityPrice"}]}},{"$unwind":"$pool"},{"$sort":{"pool.value":-1}}])
    
    def getCityStatisticData(self,nationName,cityName,statisticType):
        dollarType="$"+statisticType  
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName,"city":cityName}},{"$group":{"_id":"null","noValutation":{"$sum":{"$cond":[{"$eq":[dollarType,0.0]},1,0]}},"lowValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,0.0]},{"$lte":[dollarType,4.0]}]},1,0]}},"averageValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,4.0]},{"$lte":[dollarType,7.0]}]},1,0]}},"highValutation":{"$sum":{"$cond":[{"$gt":[dollarType,7.0]},1,0]}}}}])
    
    def getCountForUser(self,nation):
        return self.db.Hotel.aggregate([{"$match":{"nation":nation}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.reviewer","count":{"$sum":1}}}])
    
    def getNationAnalytics(self,nation):
        return self.db.Hotel.aggregate([{"$match":{"nation":nation,"position":{"$ne":0.0},"cleanliness":{"$ne":0.0},"service":{"$ne":0.0},"qualityPrice":{"$ne":0.0}}},{"$group":{"_id":"null","averagePosition":{"$avg":"$position"},"averageCleanliness":{"$avg":"$cleanliness"},"averageService":{"$avg":"$service"},"averageQualityPrice":{"$avg":"$qualityPrice"}}},{"$project":{"_id":"!null","pool":[{"name":"averagePosition","value":"$averagePosition"},{"name":"averageCleanliness","value":"$averageCleanliness"},{"name":"averageService","value":"$averageService"},{"name":"averageQualityPrice","value":"$averageQualityPrice"}]}},{"$unwind":"$pool"},{"$sort":{"pool.value":-1}}])
        
    def getNationsFromReviewer(self,reviewerName):
        return self.db.Nation.find({"reviewers":{"$in":[reviewerName]}},{"_id":0,"name":1})
    
    def getNationStatisticData(self,nationName,statisticType):
        dollarType="$"+statisticType  
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName}},{"$group":{"_id":"null","noValutation":{"$sum":{"$cond":[{"$eq":[dollarType,0.0]},1,0]}},"lowValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,0.0]},{"$lte":[dollarType,4.0]}]},1,0]}},"averageValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,4.0]},{"$lte":[dollarType,7.0]}]},1,0]}},"highValutation":{"$sum":{"$cond":[{"$gt":[dollarType,7.0]},1,0]}}}}])
    
    def getReviewsFromReviewer(self,nationName,reviewerName):
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName}},{"$unwind":{"path":"$reviewList"}},{"$match":{"reviewList.reviewer":reviewerName}},{"$project":{"name":1,"reviewList":1,"_id":0}}])
    
    def hotelOnCity(self,nationName,cityName):
        return self.db.Hotel.find({"nation":nationName,"city":cityName},{"name":1,"_id":0})
        
    def hotelOnNation(self,nationName):
        return self.db.Hotel.find({"nation":nationName},{"name":1,"_id":0})
    
    def monthInNation(self,nationName):
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month"}}])
    
    def monthCityStatistics(self,nationName,cityName):
        return self.db.Hotel.aggregate([{"$match":{"nation":nationName,"city":cityName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month","average":{"$avg":"$reviewList.vote"},"count":{"$sum":1}}}])

    def monthNationStatistics(self,entityName):
         return self.db.Hotel.aggregate([{"$match":{"nation":entityName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month","average":{"$avg":"$reviewList.vote"},"count":{"$sum":1}}}])

    def search(self,entity,entityName):
        return self.db.Hotel.count_documents({entity:entityName})
    
    def searchUser(self,username,password):
        return self.db.User.count_documents({"username":username,"password":password})

    def updateHotelOnDB(self,nationName,hotelName,newNumberVote,newAverageVote):
        self.db.Hotel.update_one({"nation":nationName,"name":hotelName},{"$set":{"numberReview":newNumberVote,"averageVote":newAverageVote}})

class middleLayer:
   
    def __init__(self):
        self.hotelAttributes = [ "name","pageLink","description","address","city","nation","numberReview","averageVote","position","cleanliness","service","qualityPrice"]
        self.reviewAttributes = [ "reviewer","text","vote","month","year" ]
        self.typeStatistics = [ "averageVote","position","cleanliness","service","qualityPrice"]
        self.classValutation = [ "none","bad","average","good"]
        self.columns = os.popen('stty size', 'r').read().split()[1]
        self.connection=Connect()
   
    def closeConnection(self):
        self.connection.close()
    
    def deleteCity(self,nation,city):
        if(self.presence("city",city)==False):
            print("Unable to delete, city not present"+"\n")
            return
        else:
            self.connection.deleteCityFromDB(nation,city)
            self.deleteUsersFromNation(nation)
            print("City deleted with success!"+"\n")
    
    def deleteHotel(self,nation,hotel):
        self.connection.deleteHotelFromDB(nation,hotel)
        self.deleteUsersFromNation(nation)
        
    def deleteNation(self,nation):
        if(self.presence("nation",nation)==False):
            print("Unable to delete, nation not present"+"\n")
            return
        else:
            self.connection.deleteNationFromDB(nation)
            print("Nation deleted with success!"+"\n")
    
    def deleteReview(self,nationAndNumber):
        splittedInformations=nationAndNumber.split(',')
        if(len(splittedInformations)!=3):
            print("Incorrent parameters passed!"+"\n")
            return 
        reviewerName=splittedInformations[0]
        nationName=splittedInformations[1]
        numberReview=0
        nationPresent=list(self.connection.getNationsFromReviewer(reviewerName))
        if(nationPresent is None):
            print("The reviewer is not present in the db"+"\n")
            return
        checkNation=False
        for nation in nationPresent:
            if(nation["name"]==nationName):
                checkNation=True
        if(checkNation==False):
            print("There aren't any review for this reviwer on the nation!"+"\n")
            return 
        try:
            numberReview=int(splittedInformations[2])
        except:
            print("Not a number,try again!")
            return 
        reviews=list(self.connection.getReviewsFromReviewer(nationName,reviewerName))
        if(numberReview<=0 or numberReview>len(reviews)):
            print("Not a number in the review list,try again!")
            return
        else:
            element=reviews[numberReview-1]
            hotelName=element["name"]
            review=element["reviewList"]
            self.connection.deleteReviewOnHotelFromDB(nationName,hotelName,reviewerName,review["month"],review["year"],review["text"])
            print("Delete with success!"+"\n")
            self.updateHotel(review["vote"],hotelName)
            if(len(reviews)==1):
                self.connection.deleteReviewerOnNationFromDB(nationName,reviewerName)
    
    def deleteReviewer(self,reviewer):
        nationPresent=list(self.connection.getNationsFromReviewer(reviewer))
        if(nationPresent is None):
            print("The reviewer is not present in the db"+"\n")
            return
        for nation in nationPresent:
            self.connection.deleteReviewerOnNationFromDB(nation,reviewer)
            reviews=list(self.connection.getReviewsFromReviewer(nation["name"],reviewer))
            for singleReview in reviews:
                hotelName=singleReview["name"]
                review=singleReview["reviewList"]               
                self.connection.deleteReviewOnHotelFromDB(nation["name"],hotelName,reviewer,review["month"],review["year"],review["text"])
                self.updateHotel(review["vote"],hotelName)
        print("Delete with success")
    
    def deleteUsersFromNation(self,nation):
        usersWithCount=list(self.connection.getCountForUser(nation))
        for user in usersWithCount:
            if(user["count"]==0):
                self.connection.deleteReviewerOnNationFromDB(nation,user["_id"])
            
    def listOfNationsFromReviewer(self,reviewerName):
        nations=[]
        nationPresent=list(self.connection.getNationsFromReviewer(reviewerName))
        for nation in nationPresent:
            nations.append(nation["name"])
        return nations
        
    def listOfReviewsFromNationAndReviewer(self,nation,reviewerName):
        reviewsOnNation=list(self.connection.getReviewsFromReviewer(nation,reviewerName))
        reviews=[]
        for review in reviewsOnNation:
            reviews.append(review["reviewList"])
        return reviews
            
    def presence(self,entityType,entityName):
        if(self.connection.search(entityType,entityName)>0):
            return True
        else:
            return False
    
    def presenceUser(self,username,password):
        if(self.connection.searchUser(username,password)>0):
            return True
        else:
            return False
    
    def printLine(self):
        print("-"*int(self.columns))
    
    def showAnalytics(self,entityName,analytics,monthStatistics):
        listAnalytics=list(analytics)
        print("Here is a list of the attribute from the most appreciated to the less in "+entityName+"\n")
        num=1
        for analytic in listAnalytics:
            print(str(num)+') ')
            stringAnalytic=analytic["pool"]
            print(stringAnalytic["name"])
            num+=1
        print("\n")
        print("Month evaluation")
        for month in monthStatistics:
            if(int(month["count"])>1 and bool(re.search(r'\d',month["_id"]))==False):
                string=("the month of "+month["_id"]+" has been evaluated in the reviews with ")
                averageVote=float(month["average"])
                if(averageVote>=8.0):
                    string+="an excellent average rating"
                elif(averageVote<8 and averageVote>=6):
                    string+="a good average rating"
                elif(averageValutation<6 and averageVote>=4):
                    string+="a medium average rating"
                elif(averageValutation<4 and averageVote>=2):
                    string+="a poor average rating"
                else:
                    string+="a terrible average rating"
                print(string)
        print("\n")
        
    def showCities(self,nationName): 
        self.printLine()
        cityList=list(self.connection.find_citiesWithCount(nationName))
        for city in cityList:
            if(city["count"]>1):
                cityName=city["_id"]
                if(isinstance(cityName,str)==True and bool("Via" in cityName)==False and bool(re.search(r'\d',cityName))==False):
                    print(cityName)
        self.printLine()
    
    def showCityAnalytics(self,nation,city):
        self.showHotelList(self.connection.hotelOnCity(nation,city))
        analytics=self.connection.getCityAnalytics(nation,city);
        monthStatistics=list(self.connection.monthCityStatistics(nation,city))
        self.showAnalytics(city,analytics,monthStatistics)
    
    def showCityStatistics(self,nationName,cityName,):
        self.showHotelList(self.connection.hotelOnCity(nationName,cityName))
        figureNumber=1
        for statisticType in self.typeStatistics:
            statistics=list(self.connection.getCityStatisticData(nationName,cityName,statisticType))
            data=[]
            data.append(statistics[0]["noValutation"])
            data.append(statistics[0]["lowValutation"])
            data.append(statistics[0]["averageValutation"])
            data.append(statistics[0]["highValutation"])
            x=range(4)
            plt.figure(figureNumber)
            #plt.bar(x,data,color='green',align='center')
            plt.title(statisticType.replace('$','')+" statistics")
            plt.xticks(x,self.classValutation,rotation='vertical')
            bars=plt.bar(x,height=data,width=.4)
            for bar in bars:
                yval=bar.get_height()
                plt.text(bar.get_x()+0.075,yval+.5,yval)
            plt.plot()
            figureNumber+=1
        plt.show()
    
    def showHotel(self,hotelName):
        dc=self.connection.find_hotel(hotelName)
        if dc is None:
                print("There isn't an hotel with this name in the database!")
        else:
            print("-"*int(self.columns))
            dimensionHotelAttributes=len(self.hotelAttributes)
            firstIndex=0
            while firstIndex<dimensionHotelAttributes-1:
                print(self.hotelAttributes[firstIndex]+ ": "+str(dc[self.hotelAttributes[firstIndex]])+"\n")
                firstIndex+=1
            print("Reviews: "+"\n")
            print("-"*int(self.columns))
            reviewList=dc["reviewList"]
            dimensionReviewAttributes=len(self.reviewAttributes)
            for review in reviewList:
                secondIndex=0
                while secondIndex<dimensionReviewAttributes:
                    print(self.reviewAttributes[secondIndex]+": "+str(review[self.reviewAttributes[secondIndex]])+"\n")
                    secondIndex+=1
                print("-"*int(self.columns))
    
    def showHotelList(self,hotelList):
        print("List of the hotel"+"\n")
        lista=list(hotelList)
        string=""
        for element in lista:
            string=(string+element["name"]+" \ ")
        print(string+"\n")
    
    def showNations(self):
        self.printLine()
        nationList=self.connection.find_nations()
        for nation in nationList:
            print(nation["name"]+"\n")
        self.printLine()
    
    def showNationAnalytics(self,nationName):
        self.showHotelList(self.connection.hotelOnNation(nationName))
        analytics=self.connection.getNationAnalytics(nationName);
        monthStatistics=list(self.connection.monthNationStatistics(nationName))
        self.showAnalytics(nationName,analytics,monthStatistics)
    
    def showNationStatistics(self,nationName):
        self.showHotelList(self.connection.hotelOnNation(nationName))
        figureNumber=1
        for statisticType in self.typeStatistics:
            statistics=list(self.connection.getNationStatisticData(nationName,statisticType))
            data=[]
            data.append(statistics[0]["noValutation"])
            data.append(statistics[0]["lowValutation"])
            data.append(statistics[0]["averageValutation"])
            data.append(statistics[0]["highValutation"])
            x=range(4)
            plt.figure(figureNumber)
            #plt.bar(x,data,color='green',align='center')
            plt.title(statisticType.replace('$','')+" statistics")
            plt.xticks(x,self.classValutation,rotation='vertical')
            bars=plt.bar(x,height=data,width=.4)
            for bar in bars:
                yval=bar.get_height()
                plt.text(bar.get_x()+0.06,yval,yval)
            plt.plot()
            figureNumber+=1
        plt.show()
    
    def showReviewsOfReviewer(self,nationName,reviewerName):
        self.reviewerName=reviewerName
        dimensionReviewAttributes=len(self.reviewAttributes)
        listElement=list(self.connection.getReviewsFromReviewer(nationName,reviewerName))
        self.reviews=[]
        index=0
        print("Nation: "+nationName)
        for element in listElement:
            print("-"*int(self.columns))
            print(str(index+1)+")")
            reviewList=element['reviewList']
            self.reviews.append(reviewList)
            for attribute in self.reviewAttributes:
                if(attribute!="reviewer"):
                    print(attribute+": "+str(reviewList[attribute])+"\n")
            index+=1
        print("-"*int(self.columns))         
    
    def updateHotel(self,lessValue,hotelName):
        print(lessValue)
        hotel=self.connection.find_hotel(hotelName)
        numberReview=int(hotel["numberReview"])
        averageVote=float(hotel["averageVote"])
        product=(numberReview*averageVote)
        newNumberReview=(numberReview-1)
        newAverageVote=((product-lessValue)/newNumberReview)
        self.connection.updateHotelOnDB(hotel["nation"],hotelName,newNumberReview,newAverageVote)
    
class frontEnd:
  
    def __init__(self):
       
        self.firstLevelCommands=["!browseNations","!findHotel","!findReviewer","!deleteHotel","!deleteReviewer","!deleteReview","!commands","!login","!logout","!quit"]
        self.firstLevelDescriptions=[": read all the nation",": search an hotel and read its informations",": search a reviewer and read its information",": delete an hotel",": delete a reviewer",": delete the review whose number is in the list of the reviews you've read",": read all the commands",": login in with your credentials","",": exit from the application"]
        self.secondLevelDescription=[ ": show the statistics of a nation of the list",": show the analytics of a nation of the list",": read the cities of a nation",": delete a nation(only if you're an admin)",": read all the commands",": login in with your credentials","",": return to the main level",": exit from the application"]  
        self.secondLevelCommands=["!showStatistics","!showAnalytics","!browseCities","!delete","!commands","!login","!logout","!back","!quit"] 
        self.thirdLevelCommands=["!showStatistics","!showAnalytics","!delete","!commands","!login","!logout","!back","!quit"]
        self.thirdLevelDescription=[ ": show the statistics of a city of the list",": show the analytics of a city of the list",": delete a city(only if you're an admin)",": read all the commands",": login in with your credentials","",": return to the nation level",": exit from the application"]       
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
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            informations=input("Insert  Nation and Hotel Name separated from , : ")
            splittedInput=informations.split(',')
            if(len(splittedInput)<2):
                print("Missing some informations!"+"\n")
            else:
                if(self.middleLayer.deleteHotel(splittedInput[0],splittedInput[1])==True):
                    print("Successfull delete!"+"\n")
                else:
                    print("Unable to delete!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[4]):
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            reviewerName=input("Insert Reviewer Name:")
            self.middleLayer.deleteReviewer(reviewerName)
            return True
        elif(commandType==self.firstLevelCommands[5]):
            if(self.typeUser=="generic"):
                print("You don't have the credentials!"+"\n")
                return True
            inputString=input("Insert reviewer, nation and review number:")
            self.middleLayer.deleteReview(inputString)
            return True
        elif(commandType==self.firstLevelCommands[6]):
            self.showCommands()
            return True
        elif(commandType==self.firstLevelCommands[7]):
            credentials=input("Insert User and Password separated from a ,"+"\n")
            splittedCredentials=credentials.split(',')
            if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                self.typeUser="admin"
                print("Login successfull")
            else:
                print("Login failed or yet done!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[8]):
            if(self.typeUser=="admin"):
                self.typeUser="generic"
                print("Logout successfull!"+"\n")
            else:
                print("You're not logged in!"+"\n")
            return True
        elif(commandType==self.firstLevelCommands[9]):
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
                if(self.middleLayer.presence("nation",nationName)==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showNationStatistics(nationName)
            elif(commandType==self.secondLevelCommands[1]):
                nationName=input("Insert the name of the nation: ")
                if(self.middleLayer.presence("nation",nationName)==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showNationAnalytics(nationName)
            elif(commandType==self.secondLevelCommands[2]):
                nationName=input("Insert the name of the nation: ")
                if(self.middleLayer.presence("nation",nationName)==False):
                    print("Nation unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCities(nationName)
                    self.level="third"
                    self.showCommands()
                    continueWhile=self.executeThirdLevelCommand(nationName)
                    if(continueWhile==False):
                        continueApplication=False
            elif(commandType==self.secondLevelCommands[3]):
                if(self.typeUser=="generic"):
                    print("You don't have the credentials to do this operation!"+"\n")
                else:
                    nationName=input("Insert the name of the nation: ")
                    self.middleLayer.deleteNation(nationName)
            elif(commandType==self.secondLevelCommands[4]):
                self.showCommands()
            elif(commandType==self.secondLevelCommands[5]):
                credentials=input("Insert User and Password separated from a ,"+"\n")
                splittedCredentials=credentials.split(',')
                if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                    self.typeUser="admin"
                    print("Login successfull")
                else:
                    print("Login failed or yet done!"+"\n")
            elif(commandType==self.secondLevelCommands[6]):
                if(self.typeUser=="admin"):
                    self.typeUser="generic"
                    print("Logout successfull!"+"\n")
                else:
                    print("You're not logged in!"+"\n")
            elif(commandType==self.secondLevelCommands[7]):
                self.level="first"
                print("Back to precedent level"+"\n")
                continueWhile=False
                continueApplication=True
            elif(commandType==self.secondLevelCommands[8]):
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
                if(self.middleLayer.presence("city",cityName)==False):
                    print("City unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCityStatistics(nation,cityName)
            elif(commandType==self.thirdLevelCommands[1]):
                cityName=input("Insert the name of the city: ")
                if(self.middleLayer.presence("city",cityName)==False):
                    print("City unknown or not inserted,try again!"+"\n")
                else:
                    self.middleLayer.showCityAnalytics(nation,cityName)
            elif(commandType==self.thirdLevelCommands[2]):
                cityName=input("Insert the name of the city: ")
                if(self.typeUser=="generic"):
                    print("You don't have the credentials to do this operation!"+"\n")
                else:
                    self.middleLayer.deleteCity(nation,cityName)
            elif(commandType==self.thirdLevelCommands[3]):
                self.showCommands()
            elif(commandType==self.thirdLevelCommands[4]):
                credentials=input("Insert User and Password separated from a ,"+"\n")
                splittedCredentials=credentials.split(',')
                if(self.typeUser=="generic" and len(splittedCredentials)==2 and self.middleLayer.presenceUser(splittedCredentials[0],splittedCredentials[1])==True):
                    self.typeUser="admin"
                    print("Login successfull")
                else:
                    print("Login failed or yet done!"+"\n")
            elif(commandType==self.thirdLevelCommands[5]):
                if(self.typeUser=="admin"):
                    self.typeUser="generic"
                    print("Logout successfull!"+"\n")
                else:
                    print("You're not logged in!"+"\n")
            elif(commandType==self.thirdLevelCommands[6]):
                print("Back to precedent level"+"\n")
                self.level="second"
                continueWhile=False
                continueApplication=True
            elif(commandType==self.thirdLevelCommands[7]):
                print("The application is closing!"+"\n")
                self.middleLayer.closeConnection()
                continueWhile=False
                continueApplication=False
            else:
                print("Unknown command,try again!"+"\n")
        return continueApplication
    
if __name__ == '__main__':

    print("Welcome to the HotelMonitoring Appliction; here are a list of all the command available: \n")
    frontEnd=frontEnd()
    frontEnd.showCommands()
    while (True):
        if not frontEnd.executeFirstLevelCommand():
            break
     
