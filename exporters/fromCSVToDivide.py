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

def main() :

    hotels=pd.read_csv("export.csv",usecols=['name','city','nation','reviews'])   
    names=hotels[['name']]
    cities=hotels[['city']]
    nations=hotels[['nation']]
    reviews=hotels[['reviews']]
    dim=len(names)
    index=0
    lastNation=""
    allReviewers=[]
    nation={}
    header=['hotel','city','nation','reviewer','vote']
    with open('dbForNeo4j.csv','a',newline='',encoding="utf-8") as f:
                    writer=csv.writer(f,delimiter=',')
                    writer.writerow(header) 
    while index<dim:    
        nationName=nations.iloc[index]['nation']       
        cityName=cities.iloc[index]['city']
        hotelName=names.iloc[index]['name']
        reviewList=reviews.iloc[index]['reviews']
        reviewList=reviewList.replace(']','')
        reviewList=reviewList.replace('[','')
        reviewsHotel=reviewList.split('}')
        for review in reviewsHotel:
            splittedReview=review.split(',')
            if(len(splittedReview)>1):
                reviewerString=splittedReview[len(splittedReview)-1]
                voteString=splittedReview[len(splittedReview)-4]
                reviewerSplitted=reviewerString.split(':')
                voteSplitted=voteString.split(':')
                if(len(reviewerSplitted)==2 and len(voteSplitted)==2):
                    reviewerName=reviewerSplitted[1].replace('"','')
                    reviewerName=reviewerName.replace('}','')
                    vote=voteSplitted[1]
                    data=[]
                    data.append(hotelName)
                    data.append(cityName)
                    data.append(nationName)
                    data.append(reviewerName)
                    data.append(vote)
                    with open('dbForNeo4j.csv','a',newline='',encoding="utf-8") as f:
                        writer=csv.writer(f,delimiter=',')
                        writer.writerow(data)
            
        index+=1
    
    
if __name__ == "__main__":
    main()
    