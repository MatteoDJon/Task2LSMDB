import numpy as np
import pandas as pd
import json 
import csv
import pickle
import difflib
import argparse
import argcomplete
import pymongo
from argcomplete.completers import ChoicesCompleter
from argcomplete.completers import EnvironCompleter
import requests
import urllib.parse
from bs4 import BeautifulSoup
import datetime


class Connection:
    def __init__(self):
        #self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.myclient=pymongo.MongoClient('mongodb://spider:spider@172.16.0.148:27020/test')    
        #self.db=self.myclient['tripbooking'] 
        self.db=self.myclient['db']

    def presence(self,nation,city,hotelName):
        return self.db.hotel.count_documents({"nation":nation,"city":city,"name":hotelName})

    def presenceNation(self,nation):
        return self.db.Nation.count_documents({"name":nation})
     
    def getAllReviewers(self,nation):
        cursor=list(self.db.Nation.find({"name":nation},{"_id":0,"reviewers":1}))
        if(cursor==[]):
            return
        listReviewers=cursor[0]
        reviewers=listReviewers['reviewers']
        returnReviewers=[]
        for reviewer in reviewers:
            returnReviewers.append(reviewer)
        return returnReviewers
     
    def getHotelInformation(self,nation,city,hotelName):
        return list(self.db.hotel.find({"nation":nation,"city":city,"name":hotelName},{"_id":0,"numberReview":1,"averageVote":1,"service":1,"qualityPrice":1,"cleanliness":1,"position":1}))
     
    def getReviews(self,nation,city,hotelName):
        return self.db.hotel.find({"nation":nation,"city":city,"name":hotelName},{"_id":0,"reviewList":1})
    
    def updateHotel(self,nation,city,hotelName,newNumberVote,newAverageVote,newPosition,newCleanliness,newService,newQualityPrice):
        self.db.hotel.update_one({"nation":nation,"city":city,"name":hotelName},{"$set":{"numberReview":newNumberVote,"averageVote":newAverageVote,"position":newPosition,"cleanliness":newCleanliness,"service":newService,"qualityPrice":newQualityPrice}})

    def updateReviewers(self,nation,reviewList):
        self.db.Nation.update_one({"name":nation},{"$set":{"reviewers":reviewList}})

    def updateReviewList(self,nation,city,hotelName,reviewList):
        self.db.hotel.update_one({"nation":nation,"city":city,"name":hotelName,"count":{"$lt":500}},{"$set":{"reviewList":reviewList},"$inc":{"count":1}},upsert=True)

    def insertHotel(self,hotel):
        self.db.hotel.insert_one(hotel)

    def insertNation(self,nation):
        self.db.Nation.insert_one(nation)
    
    def close(self):
         self.myclient.close()

def searchReviewer(allReviewers,reviewer) :
    for reviewerInList in allReviewers:
        if(reviewerInList==reviewer):
            return True
    return False

def searchReviewInReviews(list,reviewToCheck):
    found=False
    for review in list:
        if(review["text"]==reviewToCheck["text"] and review["month"]==reviewToCheck["month"] and review["year"]==reviewToCheck["year"] and review["reviewer"]==reviewToCheck["reviewer"]):
            found=True
    return found

def main() :

    #myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #myclient=pymongo.MongoClient('mongodb://spider:spider@172.16.0.148:27020/test')    
    #mydb=myclient['tripbooking']
    connection=Connection()
    hotels=pd.read_csv("booking.csv",usecols=['name','pageLink','description','address','city','nation','numberReview','averageVote','position','cleanliness','service','qualityPrice','reviews'])   
    names=hotels[['name']]
    pageLinks=hotels[['pageLink']]
    descriptions=hotels[['description']]
    numberReviews=hotels[['numberReview']]
    averageVotes=hotels[['averageVote']]
    positions=hotels[['position']]
    cleanlinessS=hotels[['cleanliness']]
    servicesS=hotels[['service']]
    qualityPrices=hotels[['qualityPrice']]
    cities=hotels[['city']]
    nations=hotels[['nation']]
    reviews=hotels[['reviews']]
    addresses=hotels[['address']]
    dim=len(names)
    index=0
    lastNation=""
    allReviewers=[]
    nation={}
    while index<dim:    
        nationName=nations.iloc[index]['nation']       
        if(lastNation!=nationName):
            if(lastNation!=""):
                    nation["reviewers"]=allReviewers
                    connection.insertNation(nation)
            lastNation=nationName
            nation={}
            nation["name"]=nationName
            allReviewers=connection.getAllReviewers(nationName)
            if allReviewers is None:
                allReviewers=[]
        cityName=cities.iloc[index]['city']
        hotelName=names.iloc[index]['name']
        if(connection.presence(nationName,cityName,hotelName)==0):
            hotel={}
            hotel["name"]=hotelName
            hotel["pageLink"]=pageLinks.iloc[index]['pageLink']
            hotel["description"]=descriptions.iloc[index]['description']
            hotel["numberReview"]=int(str(numberReviews.iloc[index]['numberReview']).replace('.',''))
            hotel["averageVote"]=averageVotes.iloc[index]['averageVote']
            hotel["position"]=positions.iloc[index]['position']
            hotel["cleanliness"]=cleanlinessS.iloc[index]['cleanliness']
            hotel["service"]=servicesS.iloc[index]['service']
            hotel["qualityPrice"]=qualityPrices.iloc[index]['qualityPrice']
            hotel["address"]=addresses.iloc[index]['address']
            hotel["city"]=cityName
            hotel["nation"]=nationName
            hotel["reviewList"]=[]
            hotel["count"]=0
            try:
                lineReview=reviews.iloc[index]['reviews']
                lineReview=lineReview.replace('[[','')
                lineReview=lineReview.replace('[','')
                lineReview=lineReview.replace(']]',']')
                parsedReviews=lineReview.split('],')
                if(lineReview!=']'):
                    for review in parsedReviews:
                        fields=review.split(',')
                        dimText=len(fields)
                        indexText=4
                        text=""
                        while(indexText<dimText):
                            text+=fields[indexText].replace("'","")
                            indexText+=1
                        d={}
                        d["text"]=text
                        d["vote"]=float(fields[3].replace("'",""))
                        d["month"]=fields[1].replace("'","")
                        d["year"]=fields[2].replace("'","")
                        reviewerName=fields[0].replace("'","")
                        d["reviewer"]=reviewerName
                        d["insertionTime"]=datetime.datetime.utcnow()
                        hotel["reviewList"].append(d)                      
                        if not searchReviewer(allReviewers,reviewerName):
                            allReviewers.append(reviewerName)
                    hotel["count"]=1
            except: 
                hotel["reviewList"].append([])            
            connection.insertHotel(hotel)
            index+=1
        else:
            informations=connection.getHotelInformation(nationName,cityName,hotelName)[0]
            if(int(str(numberReviews.iloc[index]['numberReview']).replace('.',''))>0):
                newNumberReview=(informations["numberReview"]+(int(str(numberReviews.iloc[index]['numberReview']).replace('.',''))))
            else:
                newNumberReview=informations["numberReview"]
            if((averageVotes.iloc[index]['averageVote'])*int(str(numberReviews.iloc[index]['numberReview']).replace('.',''))>0.0):    
                firstProduct=(averageVotes.iloc[index]['averageVote'])*int(str(numberReviews.iloc[index]['numberReview']).replace('.',''))
                secondProduct=(informations["numberReview"]*informations["averageVote"])
                newAverageVote=((firstProduct+secondProduct)/newNumberReview)
            else:
                newAverageVote=(informations["numberReview"]*informations["averageVote"])
            if(positions.iloc[index]['position']>0.0):    
                newPosition=((positions.iloc[index]['position']+informations["position"])/2)
            else:
                newPosition=informations["position"]
            if(cleanlinessS.iloc[index]['cleanliness']>0.0):
                newCleanliness=((cleanlinessS.iloc[index]['cleanliness']+informations["cleanliness"])/2)
            else:
                newCleanliness=informations["cleanliness"]
            if(qualityPrices.iloc[index]['qualityPrice']>0.0):
                newQualityPrice=((qualityPrices.iloc[index]['qualityPrice']+informations["qualityPrice"])/2)
            else:
                newQualityPrice=informations["qualityPrice"]
            if(servicesS.iloc[index]['service']>0.0):
                newService=((servicesS.iloc[index]['service']+informations["service"])/2)
            else:
                newService=informations["service"]
            connection.updateHotel(nationName,cityName,hotelName,newNumberReview,newAverageVote,newPosition,newCleanliness,newService,newQualityPrice)
            elements=list(connection.getReviews(nationName,cityName,hotelName))
            reviewsPresent=elements[0]["reviewList"]
            lineReview=reviews.iloc[index]['reviews']
            lineReview=lineReview.replace('[[','')
            lineReview=lineReview.replace('[','')
            lineReview=lineReview.replace(']]',']')
            parsedReviews=lineReview.split('],')
            try:
                if(lineReview!=']'):
                    for review in parsedReviews:
                        fields=review.split(',')
                        dimText=len(fields)
                        indexText=4
                        text=""
                        while(indexText<dimText):
                            text+=fields[indexText].replace("'","")
                            indexText+=1
                        d={}
                        d["text"]=text
                        d["vote"]=float(fields[3].replace("'",""))
                        d["month"]=fields[1].replace("'","")
                        d["year"]=fields[2].replace("'","")
                        reviewerName=fields[0].replace("'","")
                        d["reviewer"]=reviewerName
                        if not searchReviewInReviews(reviewsPresent,d):
                            reviewsPresent.append(d)
                            if not searchReviewer(allReviewers,reviewerName):
                                allReviewers.append(reviewerName)                   
                connection.updateReviewList(nationName,cityName,hotelName,reviewsPresent)    
            except: 
                pass
            index+=1
    if(connection.presenceNation(nationName)>0):
        connection.updateReviewers(nationName,allReviewers)
    else:
        nation["reviewers"]=allReviewers
        connection.insertNation(nation)
    connection.close()
    
if __name__ == "__main__":
    main()
