import numpy as np
import pandas as pd
import csv
import pickle
import difflib
import argparse
import argcomplete
from argcomplete.completers import ChoicesCompleter
from argcomplete.completers import EnvironCompleter
import requests
from bs4 import BeautifulSoup

def get_data(url) :
    
    try:
        r = requests.get(url, timeout=100)
    except:
        return None
    html = r.content
    parsed_html = BeautifulSoup(html, "html.parser")
    data=[]
    hotel_name=parsed_html.find('div',{'class':"ui_column is-12-tablet is-9-mobile hotels-hotel-review-atf-info-parts-ATFInfo__description--1njly"})
    if(hotel_name is None or hotel_name.find('h1') is None):
        return None
    data.append(hotel_name.find('h1').text)
    data.append(url)
    description=parsed_html.find('div',{'class':"cPQsENeY"})
    if(description is None):
        data.append("'null'")
    else:
        data.append(description.text)
    address=parsed_html.find('span',{'class',"public-business-listing-ContactInfo__nonWebLink--2rxPP public-business-listing-ContactInfo__ui_link_container--37q8W public-business-listing-ContactInfo__level_4--3JgmI"})
    if(address is None):
        data.append("'null'")
        data.append("'null'")
        data.append("'null'")
    else:
        addressStr=(address.find('span').text)
        parsedAddress=addressStr.split(',')
        beforeLast=parsedAddress[len(parsedAddress)-2]
        lastStr=parsedAddress[len(parsedAddress)-1]
        parsedLast=lastStr.split()
       
        try:
            val=int(beforeLast)
            cityStr=parsedLast[len(parsedLast)-2]
        except:
            cityStr=beforeLast
            
        
        
        try:
            data.append(parsedAddress[0])
        except:
            data.append("'null'")
        try:
           data.append(cityStr)
        except:
            data.append("'null'")
        try:
            data.append("Italia")
        except:
            data.append("'null'")
        
    numberReview=parsed_html.find('span',{'class',"hotels-hotel-review-about-with-photos-Reviews__seeAllReviews--3PpLR"})
    if(numberReview is None):
        data.append('0')
    else:
        numberReviewText=numberReview.text
        splittedNumberReview=numberReviewText.split()
        data.append(splittedNumberReview[0])
    averageReview=parsed_html.find('span',{'class',"hotels-hotel-review-about-with-photos-Reviews__overallRating--vElGA"})
    if(averageReview is None):
        data.append('0')
    else:
        averageReviewText=averageReview.text
        averageReviewStr=averageReviewText[0]
        averageReviewStr+='.'
        averageReviewStr+=averageReviewText[2]
        data.append(str(float(averageReviewStr)*2))

    valutations=parsed_html.findAll('div',{'class':"hotels-hotel-review-about-with-photos-Reviews__subratingRow--2u0CJ"})
    positionValue="null"
    cleanlinessValue="null"
    serviceValue="null"
    qualityPriceValue="null"
    if not valutations:
        data.append('0.0')
        data.append('0.0')
        data.append('0.0')
        data.append('0.0')
    else:
        for valutation in valutations:
            classValutation=(valutation.find('span').attrs['class'][1])
            String=str(classValutation)
            stringInsert=''
            stringInsert+=String[7]
            stringInsert+='.'
            stringInsert+=String[8]
            if(valutation.find('div',{'class':"hotels-hotel-review-about-with-photos-Reviews__subratingLabel--H8ZI0"}).text=="Posizione"):
                positionValue=stringInsert
            elif(valutation.find('div',{'class':"hotels-hotel-review-about-with-photos-Reviews__subratingLabel--H8ZI0"}).text=="Pulizia"):
                cleanlinessValue=stringInsert
            elif(valutation.find('div',{'class':"hotels-hotel-review-about-with-photos-Reviews__subratingLabel--H8ZI0"}).text=="Servizio"):
                serviceValue=stringInsert
            elif(valutation.find('div',{'class':"hotels-hotel-review-about-with-photos-Reviews__subratingLabel--H8ZI0"}).text=="Qualità/prezzo"):
                qualityPriceValue=stringInsert
            else :   
                pass
        try:
            data.append(str(float(positionValue)*2))
        except:
            data.append('0.0')
        try:
            data.append(str(float(cleanlinessValue)*2))
        except:
            data.append('0.0')
        try:
            data.append(str(float(serviceValue)*2))
        except:
            data.append('0.0')
        try:
            data.append(str(float(qualityPriceValue)*2))
        except:
            data.append('0.0')
            
            
    reviewArray=[]
    
    reviews=parsed_html.findAll('div',{'class':"hotels-community-tab-common-Card__card--ihfZB hotels-community-tab-common-Card__section--4r93H"})
    for review in reviews:
        dataReview=[]
        topData=review.find('div',{'class':"social-member-event-MemberEventOnObjectBlock__event_type--3njyv"})
        dataReview.append(topData.find('a').text)
        spanText=topData.find('span').text
        parsedSpan=spanText.split()
        dataReview.append(parsedSpan[len(parsedSpan)-2])
        dataReview.append(parsedSpan[len(parsedSpan)-1])
        evaluation=review.find('div',{'class':"location-review-review-list-parts-RatingLine__bubbles--GcJvM"})
        evaluationClass=(evaluation.find('span').attrs['class'][1])
        String=str(evaluationClass)
        stringInsert=''
        stringInsert+=String[7]
        stringInsert+='.'
        stringInsert+=String[8]
        dataReview.append(str(float(stringInsert)*2))
        reviewComment=review.find('div',{'class':"cPQsENeY"})
        dataReview.append(reviewComment.find('span').text)
        reviewArray.append(dataReview)
    data.append(reviewArray)
   
    with open('tripadvisor.csv','a',newline='',encoding="utf-8") as f:
        writer=csv.writer(f,delimiter=',')
        writer.writerow(data) 
        

def main() :

    
    data=[]
    df = pd.read_csv('last_hotel_links.csv')
    saved_column = df.hotelLinkHref
    for link in saved_column:
        if(link  is not None or link!=''):
            get_data(link)
    
   
    
    
if __name__ == "__main__":
    main()
    