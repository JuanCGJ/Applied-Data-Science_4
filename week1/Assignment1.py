# https://docs.python.org/3/library/re.html

# # Assignment 1

# In this assignment, you'll be working with messy medical data and using regex
#to extract relevant infromation from the data.

# Each line of the `dates.txt` file corresponds to a medical note.
#Each note has a date that needs to be extracted, but each date is
#encoded in one of many formats.

# The goal of this assignment is to correctly identify all of the
#different date variants encoded in this dataset and to properly
#normalize and sort the dates.

# Here is a list of some of the variants you might encounter in this dataset:
# A: * 04/20/2009; 04/20/09; 4/20/09; 4/3/09   ---> (r'\d{1,2}.\d{1,2}.\d{2,4}')
# E: * 6/2008; 12/2009
# F: * 2009; 2010

# B: * Mar-20-2009; Mar 20, 2009; March 20, 2009;  Mar. 20, 2009; Mar 20 2009; --->'([A-Z][a-z]{2,8}.{,2}\d{2}.{,2}\d{4})|'
#    * Mar 20th, 2009; Mar 21st, 2009; Mar 22nd, 2009
# C: * 20 Mar 2009; 20 March 2009; 20 Mar. 2009; 20 March, 2009 ---> (\d{2}.{1}[A-Z][a-z]{2,8}.{,2}\d{4})
# D: * Feb 2009; Sep 2009; Oct 2010 ---> '([A-Z][a-z]{2,8}.{,2}\d{4})|'


# Once you have extracted these date patterns from the text,
#the next step is to sort them in ascending chronological order
#accoring to the following rules:
# * Assume all dates in xx/xx/xx format are mm/dd/yy
# * Assume all dates where year is encoded in only two digits are
#   years from the 1900's (e.g. 1/5/89 is January 5th, 1989)
# * If the day is missing (e.g. 9/2009), assume it is the first day
#   of the month (e.g. September 1, 2009).
# * If the month is missing (e.g. 2010), assume it is the first of
#   January of that year (e.g. January 1, 2010).
# * Watch out for potential typos as this is a raw, real-life derived dataset.

# With these rules in mind, find the correct date in each note
# and return a pandas Series in chronological order of
# the original Series' indices.
#
# For example if the original series was this:
#
#     0    1999
#     1    2010
#     2    1978
#     3    2015
#     4    1985
#
# Your function should return this:
#
#     0    2
#     1    4
#     2    0
#     3    1
#     4    3
#
# Your score will be calculated using
#[Kendall's tau](https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient),
# a correlation measure for ordinal data.
#
# *This function should return a Series of length 500 and dtype int.*

import pandas as pd
import numpy as np
import re
from datetime import datetime


def date_sorter():

    doc = []
    with open('dates.txt') as file:
        for line in file:
            doc.append(line)

    df = pd.Series(doc)
    # print(df)

    pattern1='(\d{1,3}.\d{1,2}.\d{2,4})|'
    pattern2='([A-Z][a-z]{2,8}.{,2}\d{2}.{,2}\d{4})|'
    pattern3='(\d{2}.{1}[A-Z][a-z]{2,8}.{,2}\d{4})|'
    pattern4='([A-Z][a-z]{2,8}.{,2}\d{4})|'
    pattern5='(\d{4})'
    dates=df.str.findall(pattern1 + pattern2 + pattern3 + pattern4 + pattern5)

    # #cleaning punctual cases
    # print(dates[271])
    del dates[271][0:2]

    # saco la fecha de la tupla de 5 posiciones.
    for e,d in enumerate(dates):
        if len(d)>1: #elimino posiciones de lista de 1 al final.
            del dates[e][1:]

        for t in d[0]: #saco la informacion de la tupla(de 5 posic.)
            if len(t)>0:
                #print(t)
                dates[e]=t
        # print(e,d)

    #cleaning punctual cases
    dates[99]=dates[99][1:]
    dates[392]=dates[392][3:]
    dates[401]=dates[401][6:]
    dates[439]=dates[439][6:]
    dates[459]=dates[459][6:]
    dates[461]=dates[461][8:]
    dates[465]=dates[465][9:]
    dates[462]=dates[462][9:]
    dates[490]=dates[490][4:]

    def clean_date(x):
        x=x.replace('-', '/')
        x=re.sub(r'\W*\s', '/', x)
        #replace any noWordCharacter('.' y ',')+space by '/'
        return x
    dates=dates.apply(lambda x: clean_date(x))

    def complete_years(x):
        #agrego 19 al año que solo tiene 2 digit ej: 89 --> 1989.
        positions=re.search('\/\d{2}$', x)
        if positions != None:
            #print(positions.span()[0], positions.span()[1])
            part1=x[0:positions.span()[0]+1]
            decade='19'
            part2=x[positions.span()[0]+1:]
            x=part1+decade+part2
        return x
    dates = dates.apply(lambda x: complete_years(x))

    def reduce_letters_month(x): #reduce length of month: just 3 letters
        positions=re.search('[A-Z][a-z]+', x)
        if positions != None:
            x=re.sub(x[positions.span()[0]+3 : positions.span()[1]], '', x)
        return x
    dates=dates.apply(lambda x: reduce_letters_month(x))

    def complete_month_digits(x):#month/year line 346
        #complete month digits and add day: 1/2014 --> 01/2014

        positions=re.search('^\d\/\d{4}', x)
        if positions != None:
            x='0'+x
        return x
    dates=dates.apply(lambda x: complete_month_digits(x))

    def complete_day(x):#month/day/year:  01/2014 --> 01/01/2014
        positions=re.search('^\d{2}\/\d{4}', x)
        #line 343 a 454
        if positions != None:
            x=x[0:3]+'01/'+x[3:7]
        return x
    dates=dates.apply(lambda x: complete_day(x))

    def add_day(x):#add day 01 to the date. May/2004 --> May/01/2004
        positions=re.search('^\w{3}\/\d{4}', x)
        if positions != None:
            x=x[0:3]+'/01'+x[3:]
        return x
    dates=dates.apply(lambda x: add_day(x))

    def exchange_format(x):#exchange format 01/May/2004 --> May/01/2004
        positions=re.search('\d{2}\/[A-Z][a-z]+', x)
        if positions != None:
            x=x[3:7]+x[0:2]+x[6:]
        return x
    dates=dates.apply(lambda x: exchange_format(x))

    def add_month_day(x):#add month and day format 2004 --> 01/01/2004
        positions=re.search('^\d{4}', x)
        if positions != None:
            x='01/01/'+x
        return x
    dates=dates.apply(lambda x: add_month_day(x))

    def maping_dict(x): #lines 125 a 342

        dict_months={'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
                    'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08',
                    'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

        positions=re.search('^[A-Z].+', x)
        #print(positions)
        if positions != None:
            if x[0:3] in dict_months.keys():
                x=dict_months.get(x[0:3])+x[3:]
        return x

    dates=dates.apply(lambda x: maping_dict(x))

    def string_to_date(x): #change format to date
        x=datetime.strptime(x, '%m/%d/%Y').date()
        return x
    dates=dates.apply(lambda x: string_to_date(x))

    # [print(x,' ',y) for x,y in enumerate(dates)]
    # print('len dates: ', len(dates))
    print(dates)
    data={'Dates':dates}
    df=pd.DataFrame(data=data)
    df=df.rename_axis('index').sort_values(by=['Dates','index'], ascending=True)
    final_series=pd.Series(data=df.index)
    print(final_series)

    #return final_series
date_sorter()
