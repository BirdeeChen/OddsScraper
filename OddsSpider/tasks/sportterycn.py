import re
import time
from bs4 import BeautifulSoup
from .cndownloader_firefox import Downloader
from manager.workers import app

def cleantext(text):
    '''清理文本中多余的[]()部分，主要针对Event的主客队队名'''
    return re.sub('[\\[\\(].*?[\\]\\)]', '', text)

def isHomeFirst(bsObj):
    '''判断对阵队伍是主队在前还是客队在前，主队在前返回True，否则返回False'''
    homefirst = bsObj.find(string = '主队 VS 客队')
    awayfirst = bsObj.find(string = '客队 VS 主队')
    if homefirst and not awayfirst:
        return True
    elif not homefirst and awayfirst:
        return False
    
def getLeague(bsObj):
    # bsObj = BeautifulSoup(tag, 'html.parser')
    '''获取联赛名称（全）、简称'''
    league_tag = bsObj.find('td', class_='lname')
    if league_tag:
        try:
            return (league_tag.attrs['title'], league_tag.text)
        except KeyError:
            return (None, league_tag.text)
    else:
        print ('Error in getLeague, No such tag, check the html DOM.')
        return (None, None)

def getEventTime(bsObj):
    # bsObj = BeautifulSoup(tag, 'html.parser')
    '''获取比赛时间'''
    try:
        eventtime = bsObj.find('td', class_='lname').find_next_sibling('td').text
        if len(eventtime) == 11:#是否需要作格式化
            return (eventtime,)
        elif len(eventtime) == 10:
            return (eventtime[:5] + ' ' + eventtime[5:],)
    except AttributeError as e:
        print ('Error in getEventTime.', e)
        return (None,)

def getEvent(bsObj, homefirst):
    # bsObj = BeautifulSoup(tag, 'html.parser')
    '''获取对阵主客队名称，有主队全名、主队名、客队全名、客队名组成'''
    event = bsObj.find('td', class_='vsTd')
    if event:
        team = event.find_all('a')#针对网站结构可能的变化，选择a或是选择span
        if not team:
            team = event.find_all('span')
        if homefirst:#根据网站上主客队的顺序调整名称对应关系
            try:
                return (cleantext(team[0].attrs['title']), cleantext(team[0].text), cleantext(team[1].attrs['title']), cleantext(team[1].text))
            except KeyError:
                return (None, cleantext(team[0].text), None, cleantext(team[1].text))
        else:
            try:
                return (cleantext(team[1].attrs['title']), cleantext(team[1].text), cleantext(team[0].attrs['title']), cleantext(team[0].text))
            except KeyError:
                return (None, cleantext(team[1].text), None, cleantext(team[0].text))
    else:
        print('Error in getEvent. No such tag, check the DOM.')
        return (None, None, None, None)

@app.task(name = 'Sportterycn_Football_1X2')
def Football_1X2():
    URL = 'http://info.sporttery.cn/football/hhad_list.php'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    mapdict = {'hHeader': 'Home', 'dHeader': 'Draw', 'aHeader': 'Away'}
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    betoptions = header.find_all('span', class_='oddsHeader')
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        try:
            betodds = result.find('div', class_='hadOdds').find_all('span')
        except AttributeError as e:
            print ('Error when getting betodds.', e)
        try:
            handicap = result.find('div', class_='hadGL').text
        except AttributeError as e:
            print ('Error when getting handicap.', e)
        if betoptions and betodds and len(betoptions) == len(betodds):
            odds.extend([('Sportterycn', 'Football') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('1X2',) + (handicap, mapdict[betoptions[i].attrs['id']], betodds[i].text) for i in range(len(betoptions))])
        else:
            print('Error in Football_1X2. No such tag, check the DOM.')
    # print (odds)
    return odds

@app.task(name = 'Sportterycn_Football_1X2H')
def Football_1X2H():
    URL = 'http://info.sporttery.cn/football/hhad_list.php'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    mapdict = {'hHeader' : 'Home', 'dHeader' : 'Draw', 'aHeader' : 'Away', 'Home' : 1, 'Draw' : 1, 'Away' : -1}
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    betoptions = header.find_all('span', class_='oddsHeader')
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        try:
            betodds = result.find('div', class_ = 'hhadOdds').find_all('span')
        except AttributeError as e:
            print ('Error when getting betodds.', e)
        try:
            handicap = int(result.find('div', class_ = 'hhadGL').text)
        except AttributeError as e:
            print ('Error when getting handicap.', e)
        if betoptions and betodds and handicap and len(betoptions) == len(betodds):
            odds.extend([('Sportterycn', 'Football') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('1X2H',) + (mapdict[mapdict[betoptions[i].attrs['id']]] * handicap, mapdict[betoptions[i].attrs['id']], betodds[i].text) for i in range(len(betoptions))])
        else:
            print ('Error in Football_1X2H. No such tag, check the DOM.')
    return odds

@app.task(name='Sportterycn_Football_ttg')
def Football_ttg():
    URL = 'http://info.sporttery.cn/football/cal_ttg.htm'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        handicaps = header.find_all('span', class_='oddsHeader')
        betodds = result.find_all('span', class_='oddsItem')
        if handicaps and betodds and len(handicaps) == len(betodds):
            odds.extend([('Sportterycn', 'Football') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('TTG',) + (handicaps[i].text[:-1], 'Exact', betodds[i].text) for i in range(len(betodds))])
        else:
            print('Error in Football_ttg. No such tag, check the DOM.')
    return odds

@app.task(name='Sportterycn_Basketball_asianhandicap')
def Basketball_asianhandicap():
    URL = 'http://info.sporttery.cn/basketball/hdc_list.php'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    mapdict = {'aHeader' : 'Home', 'hHeader' : 'Away', 'Home' : 1, 'Away' : -1}
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    betoptions = header.find_all('span', class_='oddsHeader')
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        betodds = result.find_all('span', class_='oddsItem')
        try:
            handicap = float(result.find('td', class_ = 'vsTd').find('font').text[1:-1])
        except AttributeError as e:
            print ('Error in handicap.', e)
        if betodds and betoptions and len(betodds) == len(betoptions):
            odds.extend([('Sportterycn', 'Basketball') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('AsianHandicap',) + (mapdict[mapdict[betoptions[i].attrs['id']]] * handicap, mapdict[betoptions[i].attrs['id']], betodds[i].text) for i in range(len(betodds))])
        else:
            print('Error in Basketball_asianhandicap. No such tag, check the DOM.')
    return odds

@app.task(name='Sportterycn_Basketball_homeaway')
def Basketball_homeaway():
    URL = 'http://info.sporttery.cn/basketball/mnl_list.php'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    mapdict = {'aHeader' : 'Home', 'hHeader' : 'Away', 'Home' : 1, 'Away' : -1}
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    betoptions = header.find_all('span', class_ = 'oddsHeader')
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        betodds = result.find_all('span', class_='oddsItem')
        if betodds and betoptions and len(betodds) == len(betoptions):
            odds.extend([('Sportterycn', 'Basketball') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('HomeAway',) + (0, mapdict[betoptions[i].attrs['id']], betodds[i].text) for i in range(len(betodds))])
        else:
            print('Error in Basketball_asianhandicap. No such tag, check the DOM.')
    return odds

@app.task(name='Sportterycn_Basketball_overunder')
def Basketball_overunder():
    URL = 'http://info.sporttery.cn/basketball/hilo_list.php'
    D = Downloader()
    odds = []
    headertag, resulttags = D(URL)
    mapdict = {'aHeader' : 'Under', 'hHeader' : 'Over'}
    header = BeautifulSoup(headertag, 'html.parser')
    ishomefirst = isHomeFirst(header)
    betoptions = header.find_all('span', class_='oddsHeader')
    for resulttag in resulttags:
        result = BeautifulSoup(resulttag, 'html.parser')
        betodds = result.find_all('span', class_='oddsItem')
        try:
            handicap = float(result.find('label', class_ = 'rLine').text)
        except AttributeError as e:
            print ('Error in handicap.', e)
        if betodds and betoptions and len(betodds) == len(betoptions):
            odds.extend([('Sportterycn', 'Basketball') + getLeague(result) + getEvent(result, ishomefirst) + getEventTime(result) + ('OverUnder',) + (handicap, mapdict[betoptions[i].attrs['id']], betodds[i].text) for i in range(len(betodds))])
        else:
            print('Error in Basketball_asianhandicap. No such tag, check the DOM.')
    return odds

@app.task(name = 'Sportterycn_execute')
def execute_spotterycn():
    tasks = ['Sportterycn_Football_1X2', 'Sportterycn_Football_1X2H', 'Sportterycn_Football_ttg',
             'Sportterycn_Basketball_asianhandicap', 'Sportterycn_Basketball_homeaway', 'Sportterycn_Basketball_overunder']
    for task in tasks:
        # time.sleep(5)
        app.send_task(task)

if __name__ == '__main__':
    pass
    # print (Football_1X2())
    # print (Football_1X2H())
    # print (Football_ttg())
    # print (Basketball_asianhandicap())
    # print (Basketball_homeaway())
    # print (Basketball_overunder())
    
