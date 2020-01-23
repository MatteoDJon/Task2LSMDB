import pandas as pd
import csv
import pickle
import argparse
import argcomplete
from argcomplete.completers import ChoicesCompleter
from argcomplete.completers import EnvironCompleter
import requests
from bs4 import BeautifulSoup

def get_data(url) :

    try:
        r = requests.get(url, timeout=5)
    except:
        return None
    html = r.content
    parsed_html = BeautifulSoup(html, "html.parser")
    data=[]
    hotel_name=parsed_html.find('div',{'class':"hp__hotel-title"})
    if(hotel_name is None):
        return None
    hotel_text=hotel_name.find('h2').text
    parsedHotelText=hotel_text.split('\n')
    if(parsedHotelText is None):
        return None
    t=parsedHotelText[len(parsedHotelText)-2]
    data.append(t.split(',')[0])
    data.append(url)
    description=""
    descriptionText=parsed_html.find('div',{'id':"property_description_content"})
    descriptionPieces=descriptionText.findAll('p')
    for descriptionPiece in descriptionPieces:
        description+=descriptionPiece.text
    data.append(description)
    address=parsed_html.find('span',{'class':"hp_address_subtitle js-hp_address_subtitle jq_tooltip"})
    addressText=address.text
    parsedAddress=addressText.split(',')
    try:
        data.append(parsedAddress[0])
    except:
        data.append("'null'")
   
    try:
        city=parsedAddress[len(parsedAddress)-2].split()[1]
    except:
        city=parsedAddress[len(parsedAddress)-2].split()[0]
    data.append(city)
    data.append(parsedAddress[len(parsedAddress)-1].replace('\n',''))
    numberReview=parsed_html.find('div',{'class':"bui-review-score__text"})
    if(numberReview is not None):
        data.append(numberReview.text.split()[0])
    else:
        data.append('0')
    averageReview=parsed_html.find('div',{'class':"bui-review-score__badge"})
    if(averageReview is not None):
        data.append(averageReview.text.replace(',','.'))
    else:
        data.append('0.0')
    blueBars=parsed_html.findAll('li',{'class':"v2_review-scores__subscore"})
    qualityPriceValue=""
    positionValue=""
    cleanlinessValue=""
    serviceValue=""
    for bluebar in blueBars:
        typeT=bluebar.find('span',{'class':"c-score-bar__title"})
        value=bluebar.find('span',{'class':"c-score-bar__score"})
        try:
            if(typeT.text=="Rapporto qualità-prezzo"):
                qualityPriceValue=(value.text.replace(',','.'))
        except:
                qualityPrice=0.0
        try:
            if(typeT.text=="Posizione"):
                positionValue=(value.text.replace(',','.'))
        except:
                positionValue=0.0
        try:
            if(typeT.text=="Pulizia"):
                cleanlinessValue=(value.text.replace(',','.'))
        except:
                cleanlinessValue=0.0
        try:
            if(typeT.text=="Servizi"):
                serviceValue=(value.text.replace(',','.'))
        except:
                serviceValue=0.0
        
    if(positionValue!=""):
        data.append(positionValue)
    else:
        data.append(0.0)
    if(cleanlinessValue!=""):
        data.append(cleanlinessValue)
    else:
        data.append(0.0)
    if(serviceValue!=""):
        data.append(serviceValue)
    else:
        data.append(0.0)
    if(qualityPriceValue!=""):
        data.append(qualityPriceValue)
    else:
        data.append(0.0)
    allReviews=[]
    reviews=parsed_html.findAll('div',{'class':"c-review-snippet"})
    for review in reviews:
        reviewData=[]
        nameReviewer=review.find('span',{'class':"bui-avatar-block__title"})
        if(nameReviewer is None):
            reviewData.append('null')
        else:
            reviewData.append(nameReviewer.text)
        reviewData.append('null')
        reviewData.append('null')
        reviewData.append('0.0')
        textReview=review.find('span',{'class':"c-review__body"})
        if( textReview is None):
            textReview=review.find('span',{'class':"c-review__body c-review__body--original"})
        if( textReview is None):
            reviewData.append('null')
        else:
            reviewData.append(textReview.text)
        allReviews.append(reviewData)     
    data.append(allReviews)
    with open('booking.csv','a',newline='',encoding="utf-8") as f:
        writer=csv.writer(f,delimiter=',')
        writer.writerow(data) 

def main() :

    data=[]
    df = pd.read_csv('booking_hotel_links.csv')
    saved_column = df.hotelLinkHref
    for link in saved_column:
        if(link is not None):
            get_data(link)
    
if __name__ == "__main__":
    main()
