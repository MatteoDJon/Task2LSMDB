import pandas as pd
import csv
import pickle
import argparse
import argcomplete
from argcomplete.completers import ChoicesCompleter
from argcomplete.completers import EnvironCompleter
import requests
from bs4 import BeautifulSoup


def get_main_page():
    '''
    Make request to booking page and parse html
    :param offset:
    :return: html page
    '''
    
    url = 'https://www.booking.com/searchresults.it.html?label=gen173nr-1DCAEoggI46AdIM1gEaHGIAQGYARS4ARfIAQzYAQPoAQGIAgGoAgO4AvG0zu8FwAIB&sid=9267fc72e7a76cccd2705d69ebe88424&sb=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.it.html%3Flabel%3Dgen173nr-1DCAEoggI46AdIM1gEaHGIAQGYARS4ARfIAQzYAQPoAQGIAgGoAgO4AvG0zu8FwAIB%3Bsid%3D9267fc72e7a76cccd2705d69ebe88424%3Bsb_price_type%3Dtotal%26%3B&ss=Italia&is_ski_area=0&checkin_year=2019&checkin_month=12&checkin_monthday=13&checkout_year=2019&checkout_month=12&checkout_monthday=14&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&ss_raw=ital&ac_position=0&ac_langcode=it&ac_click_type=b&dest_id=104&dest_type=country&place_id_lat=43.2946&place_id_lon=12.0333&search_pageview_id=221f62f8736d0073&search_selected=true'
    r = requests.get(url, timeout=5)
    html = r.content
    parsed_html = BeautifulSoup(html, "html.parser")
    return parsed_html

def get_pages() :

    links=[]
    base_url="https://www.booking.com/searchresults.it.html?aid=304142&label=gen173nr-1DCAEoggI46AdIM1gEaHGIAQGYARS4ARfIAQzYAQPoAQGIAgGoAgO4AvG0zu8FwAIB&tmpl=searchresults&ac_click_type=b&ac_position=0&checkin_month=12&checkin_monthday=13&checkin_year=2019&checkout_month=12&checkout_monthday=14&checkout_year=2019&class_interval=1&dest_id=104&dest_type=country&from_sf=1&group_adults=2&group_children=0&label_click=undef&no_rooms=1&raw_dest_type=country&room1=A%2CA&sb_price_type=total&search_selected=1&shw_aparth=1&slp_r_match=0&src=index&src_elem=sb&srpvid=34586cac25f10065&ss=Italia&ss_raw=ital&ssb=empty&top_ufis=1&rows=25&offset="
    startoffset=25
    while startoffset<=375 :
        offsetStr=str(startoffset)
        url=base_url+offsetStr
        links.append(url)
        startoffset+=25
    return links
    
def get_hotels(url) :
    
    print(url)
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url)
    print(r.status_code)
    html=r.content
    #print(html)
    parsed_html=BeautifulSoup(html,"html.parser")
    #print(parsed_html)
    hotel_links=[]
    hotels_links=parsed_html.findAll('a',{'class':"bui-pagination__link sr_pagination_link"})
    links=[]
    for hotel_link in hotel_links:
        links.append(hotel_link['href'])
    return hotel_links
    

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
    #data.append(parsedAddress[0].replace('\n',''))
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
        if(typeT.text=="Rapporto qualità-prezzo"):
            qualityPriceValue=(value.text.replace(',','.'))
        elif(typeT.text=="Posizione"):
            positionValue=(value.text.replace(',','.'))
        elif(typeT.text=="Pulizia"):
            cleanlinessValue=(value.text.replace(',','.'))
        elif(typeT.text=="Servizi"):
            serviceValue=(value.text.replace(',','.'))
        else:
            pass
        '''
        elif(type.text=="Staff"):
            value=bluebar.find('span',{'class':"c-score-bar__score"})
            somma+=(float(value.text.replace(',','.')))
        elif(type.text=="Servizi"):
            value=bluebar.find('span',{'class':"c-score-bar__score"})
            somma+=(float(value.text.replace(',','.')))
            data.append(str(somma/2))
        '''
    data.append(positionValue)
    data.append(cleanlinessValue)
    data.append(serviceValue)
    data.append(qualityPriceValue)
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

    #with open('booking.csv','a',newline='') as f:
     #   fieldnames=['name','street','city','nation','numberReview','averageVote','service','qualityPrice','pageLink']
      #  writer=csv.writer(f,delimiter=',')
       # writer.writerow(i for i in fieldnames)
    data=[]
    df = pd.read_csv('booking_hotel_links.csv')
    saved_column = df.hotelLinkHref
    for link in saved_column:
        if(link is not None):
            get_data(link)
    
if __name__ == "__main__":
    main()
