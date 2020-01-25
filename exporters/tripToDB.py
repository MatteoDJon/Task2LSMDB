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
import random


class Connection:
    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        #self.myclient=pymongo.MongoClient('mongodb://spider:spider@172.16.0.148:27020/test')    
        self.db=self.myclient['tripbooking'] 
        #self.db=self.myclient['db']

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
     
    def getReviews(self,nation,city,hotelName):
        return self.db.hotel.find({"nation":nation,"city":city,"name":hotelName},{"_id":0,"reviewList":1})
    
    def updateHotel(self,nation,city,hotelName,newNumberVote,newAverageVote,newPosition,newCleanliness,newService,newQualityPrice):
        self.db.hotel.update_many({"nation":nation,"city":city,"name":hotelName},{"$set":{"numberReview":newNumberVote,"averageVote":newAverageVote,"position":newPosition,"cleanliness":newCleanliness,"service":newService,"qualityPrice":newQualityPrice}})

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
    fakeUser=['StefanoTDM S','usseglio','Maria L','butteflyvale','Salvatore S','Laura S','vicarioma','Rosario M','laura p','Massimo D','detectivetravel','Nikki H','Ilaria B','Alessandro','Azhaar A','Alessandro Surico','Mario Cartello','Maria T','Stefania T','Marco M']
    connection=Connection()
    hotels=pd.read_csv("tripadvisor.csv",usecols=['name','pageLink','description','address','city','nation','numberReview','averageVote','position','cleanliness','service','qualityPrice','reviews'])   
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
                    countReview=0
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
                        #d["insertionTime"]=datetime.datetime.utcnow()
                        hotel["reviewList"].append(d)
                        if not searchReviewer(allReviewers,reviewerName):
                            allReviewers.append(reviewerName)
                    count=0
                    while(count<1):
                        d={}
                        d["text"]=''
                        d["vote"]=float(random.randrange(0,10,1))
                        d["month"]='null'
                        d["year"]='null'
                        d["reviewer"]=fakeUser[int(random.randrange(0,19,1))]
                        #d["insertionTime"]=datetime.datetime.utcnow()
                        hotel["reviewList"].append(d) 
                        count+=1
                    hotel["count"]=1
            except: 
                hotel["reviewList"].append([])            
            connection.insertHotel(hotel)
            index+=1
        else:
            connection.updateHotel(nationName,cityName,hotelName,int(str(numberReviews.iloc[index]['numberReview']).replace('.','')),averageVotes.iloc[index]['averageVote'],positions.iloc[index]['position'],cleanlinessS.iloc[index]['cleanliness'],servicesS.iloc[index]['service'],qualityPrices.iloc[index]['qualityPrice'])
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
                        dataForNeo=[]
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
                        dataForNeo.append(hotelName)
                        dataForNeo.append(cityName)
                        dataForNeo.append(nationName)
                        dataForNeo.append(reviewerName)
                        dataForNeo.append(float(fields[3].replace("'","")))                       
                        if not searchReviewInReviews(reviewsPresent,d):
                            reviewsPresent.append(d)
                            if not searchReviewer(allReviewers,reviewerName):
                                allReviewers.append(reviewerName)
                        with open('updateForNeo4j.csv','a',newline='',encoding="utf-8") as f:
                            writer=csv.writer(f,delimiter=',')
                            writer.writerow(dataForNeo)
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
    