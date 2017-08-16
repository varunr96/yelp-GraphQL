#   CITY-TO-CITY COMPARISON

# -*- coding: utf-8 -*-
"""
Yelp API v2.0 code sample.
This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/documentation for the API documentation.
This program requires the Python oauth2 library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2

import statistics as stat
import numpy as np


API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'chinese'
DEFAULT_LOCATION = 'troy, michigan'
SEARCH_LIMIT = 5
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'O431yFFM6FN4KosGTFRcgA'
CONSUMER_SECRET = 'dknF9LTkRIk_6ZsGCrjNqSDXgp8'
TOKEN = 'n-FQXZAMHww5eZewJC_v9i0AxVOlBRGA'
TOKEN_SECRET = 'zgIl_9wFRYy08Oac9A8Mspa5XE4'



def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Authorization successful. Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response


def search(term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
      #  'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)
"""
def print_basic_business_info(response):
    print response['businesses'][0]['name']
    print response['businesses'][0]['location']['address']
    print response['businesses'][0]['rating']
"""
def get_average_rating(response):

    array = []

    for business in response['businesses']:
        array.append(business['rating'])

    average_rating = stat.mean(array)

    return average_rating

def get_min_index(response):

    min_val = 5.0
    min_index = -1
    i=0

    for business in response['businesses']:
        if business['rating'] < min_val:
            min_val = business['rating']
            min_index = i
        i+=1
    return min_index

def get_max_index(response):

    max_val = 1.0
    max_index = -1
    i=0

    for business in response['businesses']:
        if business['rating'] > max_val:
            max_val = business['rating']
            max_index = i
        i+=1
    return max_index

def get_medians(response):
    array = []
    result = []
    for business in response['businesses']:
        array.append(business['rating'])

    np_array = np.array(array)

    result.append(np.percentile(np_array, 25))
    result.append(np.percentile(np_array, 50))
    result.append(np.percentile(np_array, 75))

    return result

def get_stdev(response):
    array = []

    for business in response['businesses']:
        array.append(business['rating'])

    return stat.stdev(array)

def get_z_score(rating, mean, stdev):
    print type(rating)
    print type(mean)
    return ((rating - mean) / stdev)

def get_equivalent_rating(cc_rating, cc_mean, cc_stdev, hc_mean, hc_stdev):
    z = get_z_score(cc_rating, cc_mean, cc_stdev)
    return (z*hc_stdev + hc_mean)

def main():
    try:

        # hc = Home City
        hc_name = str(raw_input('Enter your home city: '))

        # cc = Current City
        cc_name = str(raw_input('Enter your current city: '))

        # Collect the Business-Type of Interest
        b_type = str(raw_input('What kind of business? (e.g. food, barbers, bars, groceries, etc.) '))

        # hcr = Home City Response
        hcr = search(b_type, hc_name)
        print hcr
        # ccr = Current City Response
        ccr = search(b_type, cc_name)



        # Collect the Five Number Summary on the Home City
        hc_mean = get_average_rating(hcr)

        # min
        hc_min_index = get_min_index(hcr)
        hc_min_rating = hcr['businesses'][hc_min_index]['rating']

        # max
        hc_max_index = get_max_index(hcr)
        hc_max_rating = hcr['businesses'][hc_max_index]['rating']

        # 1Q, median, 3Q
        medians = get_medians(hcr)
        hc_1Q = medians[0]
        hc_median = medians[1]
        hc_3Q = medians[2]

        # StDev
        hc_stdev = get_stdev(hcr)


         # Collect the Five Number Summary on the Current City
        cc_mean = get_average_rating(ccr)

        # min
        cc_min_index = get_min_index(ccr)
        cc_min_rating = ccr['businesses'][cc_min_index]['rating']

        # max
        cc_max_index = get_max_index(ccr)
        cc_max_rating = ccr['businesses'][cc_max_index]['rating']

        # 1Q, median, 3Q
        medians = get_medians(ccr)
        cc_1Q = medians[0]
        cc_median = medians[1]
        cc_3Q = medians[2]

        # StDev
        cc_stdev = get_stdev(ccr)




        print "{hcn} {btn} Stats Summary: ".format(hcn=hc_name, btn=b_type)
        print " "
        print "average: {avg}".format(avg=hc_mean)
        print "stdev: {std}".format(std=hc_stdev)
        print " "
        print " "
        print "Five-Number Summary:"
        print "min: {mr}".format(mr=hc_min_rating)
        print "25-percentile: {qr}".format(qr=hc_1Q)
        print "50-percentile: {mr}".format(mr=hc_median)
        print "75-percentile: {mr}".format(mr=hc_3Q)
        print "max: {mr}".format(mr=hc_max_rating)
        print " "
        if hc_mean > hc_median:
            print "The distribution of ratings is skewed right."
        elif hc_mean < hc_median:
            print "The distribution of ratings is skewed left."
        else:
            print "The distribution is roughly symmetrical."
        print " "
        print " "

        print "{ccn} {btn} Stats Summary: ".format(ccn=cc_name, btn=b_type)
        print " "
        print "average: {avg}".format(avg=cc_mean)
        print "stdev: {std}".format(std=cc_stdev)
        print " "
        print " "
        print "Five-Number Summary:"
        print "min: {mr}".format(mr=cc_min_rating)
        print "25-percentile: {qr}".format(qr=cc_1Q)
        print "50-percentile: {mr}".format(mr=cc_median)
        print "75-percentile: {mr}".format(mr=cc_3Q)
        print "max: {mr}".format(mr=cc_max_rating)
        print " "
        if cc_mean > cc_median:
            print "The distribution of ratings is skewed right."
        elif cc_mean < cc_median:
            print "The distribution of ratings is skewed left."
        else:
            print "The distribution is roughly symmetrical."

        print " "
        print " "
        print " "
        eg_rating = float(raw_input('Enter a rating in your current city: '))
        print "A {eg} in {ccn} is the same as a {er} in {hcn}".format(eg=eg_rating, ccn=cc_name,
         er=get_equivalent_rating(eg_rating, cc_mean, cc_stdev, hc_mean, hc_stdev), hcn=hc_name)
        print " "



    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

if __name__ == '__main__':
    main()
