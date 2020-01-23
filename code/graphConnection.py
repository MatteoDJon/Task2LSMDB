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
    
    def delete(self,type,name,optionalName):
        deleteString=""
        secondaryDelete=""
        if(type=="Nation"):
            deleteString='MATCH(hotel:Hotel{nation:"'+name+'"})<-[r:TO]-(reviewer:Reviewer) DELETE hotel,r'
            secondaryDelete='MATCH(hotel:Hotel{nation:"'+name+'"}) DELETE hotel'
        elif(type=="City"):
            deleteString='MATCH(hotel:Hotel{city:"'+name+'"})<-[r:TO]-(reviewer:Reviewer) DELETE hotel,r'
            secondaryDelete='MATCH(hotel:Hotel{city:"'+name+'"}) DELETE hotel'
        elif(type=="Reviewer"):
            deleteString='MATCH(hotel:Hotel)<-[r:TO]-(reviewer:Reviewer{name:"'+name+'"}) DELETE reviewer,r'
            secondaryDelete='MATCH(reviewer:Reviewer{name:"'+name+'"}) DELETE reviewer'
        elif(type=="Hotel"):
            deleteString='MATCH(hotel:Hotel{name:"'+name+'"})<-[r:TO]-(reviewer:Reviewer) DELETE hotel,r'
            secondaryDelete='MATCH(hotel:Hotel{name:"'+name+'"}) DELETE hotel'
        elif(type=="Review"):
            deleteString='MATCH(hotel:Hotel{name:"'+name+'"})<-[r:TO]-(reviewer:Reviewer{name:"'+optionalName+'"}) DELETE r'
        else:
            pass
        session=self.driver.session()
        session.run(deleteString)
        if(secondaryDelete!=""):
            session.run(secondaryDelete)
        session.close()
    
    def getFakeReviewer(self,nation):
        executionString="CALL algo.betweenness.stream('MATCH (reviewer:Reviewer) RETURN id(reviewer) as id','MATCH (a1:Reviewer)-[:TO]->(n:Hotel{nation:"+'"'+nation+'"'+"})<-[:TO]-(a:Reviewer) RETURN id(a) as source,id(a1) as target',{graph:'cypher'}) YIELD nodeId,centrality RETURN algo.getNodeById(nodeId).name,centrality order by centrality desc"
        session=self.driver.session()
        result=session.run(executionString)
        session.close()
        return result
    
    def getPopularHotel(self,type,parameters):
        startString='MATCH(hotel:Hotel)<-[review:TO]-(reviewer:Reviewer) WITH hotel,count(review) as c'
        parameterString=""
        if(type=="Nation"):
            parameterString=' WHERE hotel.nation="'+parameters[0]+'"'
        else:
            parameterString=' WHERE hotel.nation="'+parameters[0]+'"'+' and hotel.city="'+parameters[1]+'"'
        endString=' RETURN hotel.name ORDER BY c DESC LIMIT 30'
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
            parameterString='nation:"'+parameters[0]+'"'+',city="'+parameters[1]+'"'
        endString='})<-[review:TO]-(reviewer:Reviewer) WITH reviewer,count(review) as c RETURN reviewer.name,c ORDER BY c DESC LIMIT 30'
        totalString=(startString+parameterString+endString)
        session=self.driver.session()
        result=session.run(totalString)
        session.close()
        return result
    
    def getReccomendedHotel(self,reviewerName):
        startString='MATCH(reviewer:Reviewer)-[firstReview:TO]->(hotel:Hotel)<-[secondReview:TO]-(secondReviewer:Reviewer)-[thirdReview:TO]->(secondHotel:Hotel) WHERE reviewer.name="'
        parameterString=reviewerName+'"'
        endString='and toFloat(firstReview.vote)>7 and toFloat(secondReview.vote)>7 and toFloat(thirdReview.vote)>7 and reviewer<>secondReviewer and secondHotel<>hotel WITH reviewer,collect(secondHotel)as goodHotel UNWIND goodHotel as searchedHotel RETURN searchedHotel.name'
        totalString=(startString+parameterString+endString)
        session=self.driver.session()
        result=session.run(totalString)
        session.close()
        return result
