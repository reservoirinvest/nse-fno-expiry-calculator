import json

import pendulum
import requests
from pendulum.date import Date
import pandas as pd

headers = {
    'User-agent': 'Mozilla/5.0',
    'Accept': '/', 
    'Connection': 'keep-alive', 
    "Referer": "https://www.nseindia.com/resources/exchange-communication-holidays"
    }

def get_nse_payload(url: str) -> requests.models.Response:

    """
    Returns response

    url: (samples)
    * "https://www.nseindia.com/api/holiday-master?type=trading" ... for nse trading holidays

    Response processing examples:
    ---
    `df = pd.read_csv(io.StringIO(response.text))` for csv type response output 

    """

    base_url = 'https://www.nseindia.com'
    session = requests.Session()

    response=requests.get(url, headers=headers)

    return response


def get_nse_holidays() -> set:

    """
    Gets holidays from nse website
    """

    url = "https://www.nseindia.com/api/holiday-master?type=trading"

    r = get_nse_payload(url)

    holiday_dict = json.loads(r.text).get('CBM')
    df_nse_holidays = pd.DataFrame.from_records(holiday_dict)

    out = set(pd.to_datetime(df_nse_holidays.tradingDate).dt.date.apply(pendulum.instance))

    return out
    

def __considerHolidayList(expiryDate: Date):

    listOfNseHolidays = get_nse_holidays()

    if(expiryDate.date() in listOfNseHolidays):
        return __considerHolidayList(expiryDate.subtract(days=1))
    else:
        return expiryDate


def getNearestWeeklyExpiryDate():
    expiryDate = None
    if(pendulum.now().date().day_of_week is pendulum.THURSDAY):
        expiryDate = pendulum.now()
    else:
        expiryDate = pendulum.now().next(pendulum.THURSDAY)
    return __considerHolidayList(expiryDate).date()


def getNextWeeklyExpiryDate():
    expiryDate = None
    if(pendulum.now().date().day_of_week is pendulum.THURSDAY):
        expiryDate = pendulum.now().next(pendulum.THURSDAY)
    else:
        expiryDate = pendulum.now().next(pendulum.THURSDAY).next(pendulum.THURSDAY)
    return __considerHolidayList(expiryDate).date()


def getNearestMonthlyExpiryDate():
    expiryDate = pendulum.now().last_of('month', pendulum.THURSDAY)
    if(pendulum.now().date() > expiryDate.date()):
        expiryDate = pendulum.now().add(months=1).last_of('month', pendulum.THURSDAY)
    return __considerHolidayList(expiryDate).date()


def getNextMonthlyExpiryDate():
    expiryDate = pendulum.now().last_of('month', pendulum.THURSDAY)
    if(pendulum.now().date() > expiryDate.date()):
        expiryDate = pendulum.now().add(months=2).last_of('month', pendulum.THURSDAY)
    else:
        expiryDate = pendulum.now().add(months=1).last_of('month', pendulum.THURSDAY)
    return __considerHolidayList(expiryDate).date()

if __name__ == "__main__":
    print(getNextMonthlyExpiryDate())
# print('today is '+str(pendulum.now().date()))
# print('nearest weekly exp is '+str(getNearestWeeklyExpiryDate()))
# print('next weekly exp is '+str(getNextWeeklyExpiryDate()))
# print('nearest monthly exp is '+str(getNearestMonthlyExpiryDate()))
# print('next month exp is '+str(getNextMonthlyExpiryDate()))
