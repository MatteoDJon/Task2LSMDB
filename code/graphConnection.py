import pymongo
from datetime import datetime
from getpass import getpass
from pprint import pprint
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class GraphConnect:

    def __init__(self):
        self.driver=GraphDatabase.driver("bolt://localhost",auth=("neo4j","root"))
        #self.driver=Graph.Database.driver("bolt://172.16.0.160:7687",auth=("neo4j","LSMDB"))
    
    def delete(self,type,name,optionalName):
        deleteString=""
        secondaryDelete=""
        if(type=="Nation"):
            deleteString='MATCH(hotel:Hotel{nation:"'+name+'"})<-[review:Review]-(reviewer:Reviewer) WITH reviewer,collect(review) as itsRels FOREACH (singleReview in itsRels | SET reviewer.count=reviewer.count-1) FOREACH(singleReview in itsRels| DELETE singleReview)'            
            secondaryDelete='MATCH(hotel:Hotel{nation:"'+name+'"}) DELETE hotel'
        elif(type=="City"):
            deleteString='MATCH(hotel:Hotel{city:"'+name+'"})<-[review:Review]-(reviewer:Reviewer) WITH reviewer,collect(review) as itsRels FOREACH (singleReview in itsRels | SET reviewer.count=reviewer.count-1) FOREACH(singleReview in itsRels| DELETE singleReview)'            
            secondaryDelete='MATCH(hotel:Hotel{city:"'+name+'"}) DELETE hotel'
        elif(type=="Reviewer"):
            deleteString='MATCH(hotel:Hotel)<-[r:Review]-(reviewer:Reviewer{name:"'+name+'"}) DELETE reviewer,r'
            secondaryDelete='MATCH(reviewer:Reviewer{name:"'+name+'"}) DELETE reviewer'
        elif(type=="Hotel"):
            deleteString='MATCH(hotel:Hotel{name:"'+name+'"})<-[review:Review]-(reviewer:Reviewer) WITH reviewer,collect(review) as itsRels FOREACH (singleReview in itsRels | SET reviewer.count=reviewer.count-1) FOREACH(singleReview in itsRels| DELETE singleReview)'               
            secondaryDelete='MATCH(hotel:Hotel{name:"'+name+'"}) DELETE hotel'
        elif(type=="Review"):
            deleteString='MATCH(hotel:Hotel{name:"'+name+'"})<-[review:Review]-(reviewer:Reviewer{name:"'+optionalName+'"}) SET reviewer.count=reviewer.count-1 DELETE review'
        else:
            pass
        session=self.driver.session()
        session.run(deleteString)
        if(secondaryDelete!=""):
            session.run(secondaryDelete)
        session.close()
    
    def getFakeReviewer(self,nation):
        executionString="CALL algo.betweenness.stream('MATCH (reviewer:Reviewer) RETURN id(reviewer) as id','MATCH (a1:Reviewer)-[:Review]->(n:Hotel{nation:"+'"'+nation+'"'+"})<-[:Review]-(a:Reviewer) RETURN id(a) as source,id(a1) as target',{graph:'cypher'}) YIELD nodeId,centrality RETURN algo.getNodeById(nodeId).name,centrality order by centrality desc LIMIT 20"
        session=self.driver.session()
        result=session.run(executionString)
        session.close()
        return result
    
    def getPopularHotel(self,type,parameters):
        startString='MATCH(hotel:Hotel'
        parameterString=""
        if(type=="Nation"):
            parameterString='{nation:"'+parameters[0]+'"'
        else:
            parameterString='{nation:"'+parameters[0]+'"'+',city:"'+parameters[1]+'"'
        endString='})<-[review:Review]-(reviewer:Reviewer) RETURN hotel.name,count(review) as countHotel ORDER by countHotel desc limit 50'
        totalString=(startString+parameterString+endString)
        session=self.driver.session()
        result=session.run(totalString)
        session.close()
        return result
    
    def getPopularReviewer(self,type,parameters):
        startString='MATCH(hotel:Hotel{'
        parameterString=""
        if(type=="Nation"):
            parameterString='nation:"'+parameters[0]+'"'
        else:
            parameterString='nation:"'+parameters[0]+'"'+',city:"'+parameters[1]+'"'
        endString='})<-[review:Review]-(reviewer:Reviewer) WITH distinct reviewer.name as nameReviewer,reviewer.count as countReviewer ORDER BY countReviewer desc RETURN nameReviewer limit 50'
        totalString=(startString+parameterString+endString)
        session=self.driver.session()
        result=session.run(totalString)
        session.close()
        return result
    
    def getReccomendedHotel(self,reviewerName):
        startString='MATCH(reviewer:Reviewer)-[firstReview:Review]->(hotel:Hotel)<-[secondReview:Review]-(secondReviewer:Reviewer)-[thirdReview:Review]->(secondHotel:Hotel) WHERE reviewer.name="'
        parameterString=reviewerName+'"'
        endString='and toFloat(firstReview.vote)>7 and toFloat(secondReview.vote)>7 and toFloat(thirdReview.vote)>7 and reviewer<>secondReviewer and secondHotel<>hotel WITH reviewer,collect(secondHotel)as goodHotel UNWIND goodHotel as searchedHotel RETURN searchedHotel.name LIMIT 10'
        totalString=(startString+parameterString+endString)
        session=self.driver.session()
        result=session.run(totalString)
        session.close()
        return result
