from connect import Connect
from graphConnection import GraphConnect
import pymongo
from datetime import datetime
from getpass import getpass
from pprint import pprint
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class middleLayer:
   
    def __init__(self):
        self.hotelAttributes = [ "name","pageLink","description","address","city","nation","numberReview","averageVote","position","cleanliness","service","qualityPrice"]
        self.reviewAttributes = [ "reviewer","text","vote","month","year" ]
        self.typeStatistics = [ "averageVote","position","cleanliness","service","qualityPrice"]
        self.classValutation = [ "none","bad","average","good"]
        self.columns = os.popen('stty size', 'r').read().split()[1]
        self.connection=Connect()
        self.graphConnection=GraphConnect()
   
    def callSwitchConnection(self,type):
        self.connection.switchConnection(type)
   
    def closeConnection(self):
        self.connection.close()
    
    def deleteCity(self,nation,city):
        if(self.presence("city",nation,city)==False):
            print("Unable to delete, city not present"+"\n")
            return
        else:
            self.connection.deleteCityFromDB(nation,city)
            self.deleteUsersFromNation(nation)
            print("City deleted with success!"+"\n")
    
    def deleteHotel(self,nation,hotel):
        self.connection.deleteHotelFromDB(nation,hotel)
        self.deleteUsersFromNation(nation)
    
    def deleteOnGraphDB(self,type,name,optionalName):
        self.graphConnection.delete(type,name,optionalName)
        
    def deleteNation(self,nation):
        if(self.presence("nation",nation,"")==False):
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
            self.deleteOnGraphDB("Review",hotelName,reviewerName)
            print("Delete with success!"+"\n")
            self.updateHotel(review["vote"],hotelName)
            if(len(reviews)==1):
                self.connection.deleteReviewerOnNationFromDB(nationName,reviewerName)
                self.deleteOnGraphDB("Reviewer",reviewerName,"")
    
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
            
    def presence(self,entityType,nation,accessoryCity):
        if(entityType=="Nation"):
            count=self.connection.searchNation(nation)
        else:
            count=self.connection.searchCity(nation,accessoryCity)
        if(count>0):
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
            if(isinstance(month["_id"],str)==True and int(month["count"])>1 and bool(re.search(r'\d',month["_id"]))==False and bool(re.search('null',month["_id"]))==False):
                string=("the month of "+month["_id"]+" has been evaluated in the reviews with ")
                averageVote=float(month["average"])
                if(averageVote>=8.0):
                    string+="an excellent average rating"
                elif(averageVote<8 and averageVote>=6):
                    string+="a good average rating"
                elif(averageVote<6 and averageVote>=4):
                    string+="a medium average rating"
                elif(averageVote<4 and averageVote>=2):
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
    
    def showFakeReviewer(self,nation):
        result=self.graphConnection.getFakeReviewer(nation)
        self.printLine()
        count=0
        for record in result:
            if(record["centrality"]==0):
                break
            else:
                print(record["algo.getNodeById(nodeId).name"])
                count+=1
        if(count==0):
            print("No fake user detected")
        else:
            pass
        self.printLine()
    
    def showHotel(self,hotelName):
        listHotel=list(self.connection.find_hotel(hotelName))
        for dc in listHotel:
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
    
    def showPopularHotel(self,type,parameters):
        result=self.graphConnection.getPopularHotel(type,parameters)
        count=0
        self.printLine()
        for record in result:
            print(record["hotel.name"])
            count+=1
        if(count==0 and type=="Nation"):
            print("Nation non existing")
        elif(count==0 and type=="City"):
            print("City non existing")
        else:
            pass
        self.printLine()
    
    def showPopularReviewer(self,type,parameters):
        result=self.graphConnection.getPopularReviewer(type,parameters)
        count=0
        self.printLine()
        for record in result:
            print(record["nameReviewer"])
            count+=1
        if(count==0 and type=="Nation"):
            print("Nation non existing")
        elif(count==0 and type=="City"):
            print("City non existing")
        else:
            pass
        self.printLine()
    
    def showReccomendedHotel(self,reviewerName):
        result=self.graphConnection.getReccomendedHotel(reviewerName)
        count=0
        self.printLine()
        for record in result:
            print(record["searchedHotel.name"])
            count+=1
        if(count==0):
            print("No reccomended hotel or user not present")
        else:
            pass
        self.printLine()
     
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
        hotel=self.connection.find_hotel(hotelName)
        numberReview=int(hotel["numberReview"])
        averageVote=float(hotel["averageVote"])
        product=(numberReview*averageVote)
        newNumberReview=(numberReview-1)
        newAverageVote=((product-lessValue)/newNumberReview)
        self.connection.updateHotelOnDB(hotel["nation"],hotelName,newNumberReview,newAverageVote)
    