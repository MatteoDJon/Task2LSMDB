import pymongo
from datetime import datetime
from getpass import getpass
from pprint import pprint
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class Connect:

    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        #self.myclient=pymongo.MongoClient('mongodb://application:application@172.16.0.148:27020/test')    
        self.db=self.myclient['tripbooking'] 
        #self.db=self.myclient['db']
        
    def close(self):
        if self.myclient != "":
            self.myclient.close()
    
    def deleteCityFromDB(self,nation,city):
        return self.db.hotel.delete_many({"nation":nation,"city":city})
    
    def deleteHotelFromDB(self,nation,hotel):
        return self.db.hotel.delete_many({"nation":nation,"name":hotel})
    
    def deleteNationFromDB(self,entityName):
        self.db.hotel.delete_many({"nation":entityName})
        self.db.Nation.delete_one({"name":entityName})
            
    def deleteReviewerOnNationFromDB(self,nationName,reviewerName):
        self.db.Nation.update_one({"name":nationName},{"$pull":{"reviewers":reviewerName}})
    
    def deleteReviewOnHotelFromDB(self,nationName,hotelName,reviewer,month,year,text):
        return self.db.hotel.update_one({"nation":nationName,"name":hotelName},{"$pull":{"reviewList":{"reviewer":reviewer,"month":month,"year":year,"text":text}}})
    
    def find_hotel(self,hotelName):
        return self.db.hotel.find({"name":hotelName})
    
    def find_nations(self):
        return self.db.Nation.find({},{"name":1,"_id":0})
    
    def find_citiesWithCount(self,nationName):
        return self.db.hotel.aggregate([{"$match":{"nation":nationName}},{"$group":{"_id":"$city","count":{"$sum":1}}}])

    def getCityAnalytics(self,nation,city):
        return self.db.hotel.aggregate([{"$match":{"nation":nation,"city":city,"position":{"$ne":0.0},"cleanliness":{"$ne":0.0},"service":{"$ne":0.0},"qualityPrice":{"$ne":0.0}}},{"$group":{"_id":"null","averagePosition":{"$avg":"$position"},"averageCleanliness":{"$avg":"$cleanliness"},"averageService":{"$avg":"$service"},"averageQualityPrice":{"$avg":"$qualityPrice"}}},{"$project":{"_id":"!null","pool":[{"name":"averagePosition","value":"$averagePosition"},{"name":"averageCleanliness","value":"$averageCleanliness"},{"name":"averageService","value":"$averageService"},{"name":"averageQualityPrice","value":"$averageQualityPrice"}]}},{"$unwind":"$pool"},{"$sort":{"pool.value":-1}}])
    
    def getCityStatisticData(self,nationName,cityName,statisticType):
        dollarType="$"+statisticType  
        return self.db.hotel.aggregate([{"$match":{"nation":nationName,"city":cityName}},{"$group":{"_id":"null","noValutation":{"$sum":{"$cond":[{"$eq":[dollarType,0.0]},1,0]}},"lowValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,0.0]},{"$lte":[dollarType,4.0]}]},1,0]}},"averageValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,4.0]},{"$lte":[dollarType,7.0]}]},1,0]}},"highValutation":{"$sum":{"$cond":[{"$gt":[dollarType,7.0]},1,0]}}}}])
    
    def getCountForUser(self,nation):
        return self.db.hotel.aggregate([{"$match":{"nation":nation}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.reviewer","count":{"$sum":1}}}])
    
    def getNationAnalytics(self,nation):
        return self.db.hotel.aggregate([{"$match":{"nation":nation,"position":{"$ne":0.0},"cleanliness":{"$ne":0.0},"service":{"$ne":0.0},"qualityPrice":{"$ne":0.0}}},{"$group":{"_id":"null","averagePosition":{"$avg":"$position"},"averageCleanliness":{"$avg":"$cleanliness"},"averageService":{"$avg":"$service"},"averageQualityPrice":{"$avg":"$qualityPrice"}}},{"$project":{"_id":"!null","pool":[{"name":"averagePosition","value":"$averagePosition"},{"name":"averageCleanliness","value":"$averageCleanliness"},{"name":"averageService","value":"$averageService"},{"name":"averageQualityPrice","value":"$averageQualityPrice"}]}},{"$unwind":"$pool"},{"$sort":{"pool.value":-1}}])
        
    def getNationsFromReviewer(self,reviewerName):
        return self.db.Nation.find({"reviewers":{"$in":[reviewerName]}},{"_id":0,"name":1})
    
    def getNationStatisticData(self,nationName,statisticType):
        dollarType="$"+statisticType  
        return self.db.hotel.aggregate([{"$match":{"nation":nationName}},{"$group":{"_id":"null","noValutation":{"$sum":{"$cond":[{"$eq":[dollarType,0.0]},1,0]}},"lowValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,0.0]},{"$lte":[dollarType,4.0]}]},1,0]}},"averageValutation":{"$sum":{"$cond":[{"$and":[{"$gt":[dollarType,4.0]},{"$lte":[dollarType,7.0]}]},1,0]}},"highValutation":{"$sum":{"$cond":[{"$gt":[dollarType,7.0]},1,0]}}}}])
    
    def getReviewsFromReviewer(self,nationName,reviewerName):
        return self.db.hotel.aggregate([{"$match":{"nation":nationName}},{"$unwind":{"path":"$reviewList"}},{"$match":{"reviewList.reviewer":reviewerName}},{"$project":{"name":1,"reviewList":1,"_id":0}}])
    
    def hotelOnCity(self,nationName,cityName):
        return self.db.hotel.find({"nation":nationName,"city":cityName},{"name":1,"_id":0})
        
    def hotelOnNation(self,nationName):
        return self.db.hotel.find({"nation":nationName},{"name":1,"_id":0})
    
    def monthInNation(self,nationName):
        return self.db.hotel.aggregate([{"$match":{"nation":nationName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month"}}])
    
    def monthCityStatistics(self,nationName,cityName):
        return self.db.hotel.aggregate([{"$match":{"nation":nationName,"city":cityName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month","average":{"$avg":"$reviewList.vote"},"count":{"$sum":1}}}])

    def monthNationStatistics(self,entityName):
         return self.db.hotel.aggregate([{"$match":{"nation":entityName}},{"$unwind":"$reviewList"},{"$group":{"_id":"$reviewList.month","average":{"$avg":"$reviewList.vote"},"count":{"$sum":1}}}])

    def searchCity(self,nation,city):
        return self.db.hotel.count_documents({"nation":nation,"city":city})
    
    def searchNation(self,nation):
        return self.db.hotel.count_documents({"nation":nation})
    
    def searchUser(self,username,password):
        return self.db.User.count_documents({"username":username,"password":password})
    
    def switchConnection(self,type):
        self.close()
        if(type=="generic"):
                self.myclient=pymongo.MongoClient('mongodb://admin:admin@172.16.0.148:27020/test')
        else:
                self.myclient=pymongo.MongoClient('mongodb://application:application@172.16.0.148:27020/test')
    
    def updateHotelOnDB(self,nationName,hotelName,newNumberVote,newAverageVote):
        self.db.hotel.update_many({"nation":nationName,"name":hotelName},{"$set":{"numberReview":newNumberVote,"averageVote":newAverageVote}})
