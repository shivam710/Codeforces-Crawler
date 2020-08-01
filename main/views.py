from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
import re
from urllib.request import urlopen
from .forms import HandleForm
from django.views.generic import TemplateView
import requests
from bs4 import BeautifulSoup
from . import fusioncharts
import pandas as pd
from matplotlib import pyplot as plt
from .models import *
from collections import OrderedDict
import mpld3
from django.contrib.auth import get_user_model
User = get_user_model()

def home(request):
    return render(request, 'home.html', {})

def contact(request):
    return render(request, 'contact.html', {})

def cfhandle(request):
    if request.method == 'POST':
        form = HandleForm(request.POST)
        if form.is_valid():
            handle = form.cleaned_data.get('handle')
            return redirect('/cfhandle/' + handle)
    else:
        form = HandleForm()

    return render(request, 'searchhandle.html', {'form': form})

def time_table(request):
    
    return render(request, 'time_table.html', {})

def code_forces(request):
    url="https://codeforces.com/contests"
    page=requests.get(url)
    bs=BeautifulSoup(page.content, 'html.parser')

    tables=bs.find_all('table', class_="")
    dic=[]

    sec=tables[0].find_all('tr')
    for item in sec:
        secx=item.find_all('td')
        secx=[x.text.strip() for x in secx]

        if len(secx)>0:
            if secx[1] == '':
                secx[1] = "Not Mentioned"
            dic.append(secx)


    return render(request, 'cf.html', {'dic':dic})

def code_chef(request):
    url="https://www.codechef.com/contests"
    page=requests.get(url)
    bs=BeautifulSoup(page.content, 'html.parser')
    tables=bs.find_all('table', class_="dataTable")
    
    dic1=[]
    dic2=[]
    
    sec=tables[0].find_all('tr')
    for item in sec:
        secx=item.find_all('td')
        secx=[x.text.strip() for x in secx]

        if len(secx)>0:
            dic1.append(secx)

    sec=tables[1].find_all('tr')
    for item in sec:
        secx=item.find_all('td')
        secx=[x.text.strip() for x in secx]

        if len(secx)>0:
            dic2.append(secx)
            
    return render(request, 'cchef.html', {'dic1':dic1,'dic2':dic2})

def who(request, handle):
    context = {
        'handle': handle,
    }
    start_url = "https://www.codeforces.com/"
    print(handle)
    cf_handle = handle
    contests_url = start_url + 'profile/' + cf_handle
    print(contests_url)
    page = requests.get(contests_url)
    soup = BeautifulSoup(page.content, 'lxml')

    title = soup.find('title').text
    print(title)
    if title == 'Codeforces':
        form = HandleForm()
        return render(request, 'searchhandle.html', {'form': form, 'error': 'invalid handle case sensitive'})



    return render(request, 'options.html', context)


# def submission(request, handle):
#     friend = handle
#     p_link = "https://codeforces.com/api/user.status?handle="
#     r = requests.get(p_link + friend)
#     data = r.json()
#     accepted = 0
#     wrong_answer = 0
#     time_exceed = 0
#     runtime_error = 0
#     hacked = 0
#     compilation_error = 0
#     submissions = {}
#     today = date.today()
#     for rows in data['result']:
#         time = rows['creationTimeSeconds']
#         s_day = datetime.fromtimestamp(time).date()
#         days = (today - s_day).days
#         week = days // 7
#         day = days % 7 + 1
#         if week <= 3:
#             if submissions.get(week) is None:
#                 submissions[week] = {day: 1}
#             else:
#                 dic = submissions[week]
#                 if dic.get(day) is None:
#                     dic[day] = 1
#                 else:
#                     dic[day] += 1
#         if rows.get('verdict') is not None:
#             verdict = rows['verdict']
#             if verdict == "OK":
#                 accepted += 1
#             elif verdict == "HACKED":
#                 hacked += 1
#             elif verdict == "WRONG_ANSWER":
#                 wrong_answer += 1
#             elif verdict == "TIME_LIMIT_EXCEEDED":
#                 time_exceed += 1
#             elif verdict == "RUNTIME_ERROR":
#                 runtime_error += 1
#             else:
#                 compilation_error += 1
#
#     for key in submissions:
#         dic = submissions[key]
#         for i in range(1, 8):
#             if dic.get(i) is None:
#                 dic[i] = 0
#
#     context = {
#         'handle': handle,
#         'accepted': accepted,
#         'hacked': hacked,
#         'runtime_error': runtime_error,
#         'wrong_answer': wrong_answer,
#         'time_exceed': time_exceed,
#         'compilation_error': compilation_error,
#     }
#     for key in submissions:
#         dic = submissions[key]
#         for i in range(1, 8):
#             context['day' + str(key) + str(i)] = dic[i]
#     print(context)
#     return render(request, "sub_stats.html", context)


# def contest(request, handle):
#     page_url = "https://codeforces.com/api/user.rating?handle=" + handle
#     r = requests.get(page_url)
#     data = r.json()
#     contests = []
#     ranks = []
#     for i in data['result']
#         contests.append(i['contestId'])
#         ranks.append(i['rank'])
#     context = {
#         'handle': handle,
#         'contests': contests,
#         'ranks': ranks,
#     }
#
#     return render(request, "contest_stats.html", context)
#


def contest(request,handle):

    fcs = fetch_contest_stats(handle)
    chart = {"output_languages" :  display_stats_languages(handle).render(),
            "output_verdicts" :  display_stats_verdicts(handle).render(),
            "output_levels" :  display_stats_levels(handle).render(),
    }
    fcs.update(chart)

    return render(request, 'contest_stats.html', fcs)

    fcs = fetch_contest_stats(handle)
    submissionsFigure(request)

    return render(request, 'figure_html.html', fcs)

def fetch_contest_stats(handle):
    start_url = "https://www.codeforces.com/"

    cf_handle = handle
    contests_url = start_url+'contests/with/'+cf_handle

    page = requests.get(contests_url)
    soup = BeautifulSoup(page.content, 'lxml')


    table = soup.find('table', class_='tablesorter user-contests-table')
    tbody = table.find('tbody')

    ROWS = tbody.find_all('tr')

    delta_rating = []
    rank_list = []

    for item in ROWS:
        elements = item.find_all('td')
        rank = int(elements[2].find('a').text)
        rating_change = int(elements[4].text)

        delta_rating.append(rating_change)
        rank_list.append(rank)

    delta_rating.sort()
    rank_list.sort()

    mydict = {
        'Handle' : cf_handle,
        'No_of_Contests' : ROWS[0].find('td').text,
        'Best_Rank' : rank_list[0],
        'Worst_Rank' : rank_list[len(rank_list)-1],
        'Max_Up' : delta_rating[len(delta_rating)-1],
        'Max_Down' : delta_rating[0],
    }

    return mydict

def search_handle(request):
    if request.method == "POST":
        form = HandleForm(request.POST)


        if form.is_valid():
            handle = form.cleaned_data["cf_handle"]
            # print(handle)

            fcs = fetch_contest_stats(handle)
            chart = {"output_languages" :  display_stats_languages(handle).render(),
                    "output_verdicts" :  display_stats_verdicts(handle).render(),
                    "output_levels" :  display_stats_levels(handle).render(),
            }

            fcs.update(chart)

            return render(request, 'login/contest_stats.html', fcs)

    else :
        form = HandleForm()

    form = HandleForm()

    return render(request, 'login/search.html', {"form":form})

def get_submission_stats(handle):
    languages.objects.all().delete()
    verdicts.objects.all().delete()
    levels.objects.all().delete()

    page = requests.get("https://codeforces.com/submissions/" + handle)

    soup = BeautifulSoup(page.content, 'lxml')
    div = soup.find_all('div', class_='pagination')

    if len(div) == 1:
        t=1

    else:
        ul = div[1].find('ul')
        li = ul.find_all('li')

        t = int(li[-2].text)


    val = pd.Series()
    verd = pd.Series()
    lev = pd.Series()

    for i in range(t):
        p = pd.read_html("https://codeforces.com/submissions/" + handle + "/page/" + str(i+1))
        table = p[5]

        val = val.combine(table['Lang'].value_counts(),(lambda x1, x2 : x1+x2), fill_value=0)
        verd = verd.combine(table['Verdict'].value_counts(),(lambda x1, x2 : x1+x2), fill_value=0)
        lev = lev.combine(table['Problem'].value_counts(),(lambda x1, x2 : x1+x2), fill_value=0)

    labels_lang = val._index
    labels_verd = verd._index
    labels_lev = lev._index


    for l in labels_lang:
        a = languages.objects.update_or_create(name = l, val = val[l])[0]
        a.save()

    for l in labels_verd:
        a = verdicts.objects.update_or_create(name = l, val = verd[l])[0]
        a.save()

    for l in labels_lev:
        a = levels.objects.update_or_create(name = l, val = lev[l])[0]
        a.save()


def display_stats_languages(handle):
    get_submission_stats(handle)

    chartConfig = OrderedDict()
    chartConfig["caption"] = "Languages of " + handle
    chartConfig["xAxisName"] = "Languages"
    chartConfig["xAxisName"] = "Submissions"
    chartConfig["theme"] = "fusion"
    chartConfig["animation"] = ""

    datasource = OrderedDict()
    datasource["Chart"] = chartConfig
    datasource["data"] = []
    # print(languages.objects.all())
    for l in languages.objects.all():
        datasource["data"].append({"label": l.name, "value": str(l.val)})

    graph2D = fusioncharts.FusionCharts("pie2d", "Languages Chart", "600", "400", "languages_chart", "json", datasource)

    return graph2D

def display_stats_verdicts(handle):

    chartConfig = OrderedDict()
    chartConfig["caption"] = "Verdicts of " + handle
    chartConfig["xAxisName"] = "Verdicts"
    chartConfig["xAxisName"] = "Submissions"
    chartConfig["theme"] = "fusion"
    chartConfig["animation"] = ""

    datasource = OrderedDict()
    datasource["Chart"] = chartConfig
    datasource["data"] = []

    WA = 0
    AC = 0
    RTE = 0
    MLE = 0
    CE = 0
    TLE = 0

    for l in verdicts.objects.all():
        item = l.name
        if item[:5] == "Wrong":
            WA += l.val

        elif item[:5] == "Time":
            TLE += l.val

        elif item == "Accepted":
            AC += l.val

        elif item[:6] == "Memory":
            MLE += l.val

        elif item[:11] == "Compilation":
            CE += l.val

        elif item[:7] == "Runtime":
            RTE += l.val

    datasource["data"].append({"label": "Accepted", "value": AC})
    datasource["data"].append({"label": "Wrong Answer", "value": WA})
    datasource["data"].append({"label": "Runtime Error", "value": RTE})
    datasource["data"].append({"label": "Memory Limit Exceeded", "value": MLE})
    datasource["data"].append({"label": "Compilation Error", "value": CE})
    datasource["data"].append({"label": "Time Limit Exceeded", "value": TLE})

    graph2D = fusioncharts.FusionCharts("pie2d", "Verdicts Chart", "700", "500", "verdicts_chart", "json", datasource)

    return graph2D

def display_stats_levels(handle):

    chartConfig = OrderedDict()
    chartConfig["caption"] = "Levels of " + handle
    chartConfig["xAxisName"] = "Levels"
    chartConfig["xAxisName"] = "Submissions"
    chartConfig["theme"] = "fusion"
    chartConfig["animation"] = ""

    datasource = OrderedDict()
    datasource["Chart"] = chartConfig
    datasource["data"] = []

    A = 0
    B = 0
    C = 0
    D = 0
    E = 0
    R = 0

    for l in levels.objects.all():
        item = l.name
        if item[0] == "A":
            A += l.val

        elif item[0] == "B":
            B += l.val

        elif item[0] == "C":
            C += l.val

        elif item[0] == "D":
            D += l.val

        elif item[0] == "E":
            E += l.val

        else:
            R += l.val

    datasource["data"].append({"label": "A", "value": A})
    datasource["data"].append({"label": "B", "value": B})
    datasource["data"].append({"label": "C", "value": C})
    datasource["data"].append({"label": "D", "value": D})
    datasource["data"].append({"label": "E", "value": E})
    datasource["data"].append({"label": "R", "value": R})


    graph2D = fusioncharts.FusionCharts("column2d", "Levels Chart", "700", "500", "levels_chart", "json", datasource)

    return graph2D

def iitg(request):
    url1 = "https://codeforces.com/ratings/organization/297"
    page1 = requests.get(url1)
    soup1 = BeautifulSoup(page1.content, 'lxml')
    div1 = soup1.find_all('div', class_='pagination')

    if len(div1) == 1:
        t = 1
    else:
        ul = div1[1].find('ul')
        li = ul.find_all('li')

        t = int(li[-2].text)

    dic = []
    for i in range(t + 1):
        url = "https://codeforces.com/ratings/organization/297/page/" + str(i+1)
        # print(url)
        page = requests.get(url)
        bs = BeautifulSoup(page.content, 'lxml')
        div = bs.find_all('div',class_='datatable ratingsDatatable')
        # print(div)
        tables = div[0].find_all('table')

        sec=tables[0].find_all('tr')
        for item in sec:
            secx = item.find_all('td')

            if len(secx) == 0:
                continue
            list = []
            stri = secx[0].text.strip()
            r = 0
            for e in stri:
                if e =='(':
                    break
                if e>='0' and e<='9':
                    r = r*10 + int(e)
            if r==0:
                continue
            list.append(r)
            list.append(secx[1].text.strip())
            list.append(sec[1].find_all('a')[0]['class'][1])
            list.append(secx[2].text.strip())
            list.append(secx[3].text.strip())
            dic.append(list)
    print(dic)
    return render(request, 'iitg.html', {'dic':dic})

def allchat(request):
    alluser = User.objects.all()
    return render(request, 'allchat.html', {'alluser': alluser})

def chatroom(request, userid1, userid2):
    userid1 = int(userid1)
    userid2 = int(userid2)

    if userid1 > userid2:
        userid1,userid2 = userid2,userid1
    print(userid1,userid2)

    user1_ = User.objects.get(pk=userid1)
    user2_ = User.objects.get(pk=userid2)

    print(user1_, user2_)

    try:
        chatroom = Chatroom.objects.get(user1=user1_, user2=user2_)
    except Chatroom.DoesNotExist:
        chatroom = Chatroom.objects.create(user1=user1_, user2=user2_)
        chatroom.save()


    messages = Chatmessage.objects.filter(chatroom=chatroom)
    print(chatroom)
    print(messages)
    # return render(request, 'home.html', {})
    return render(request, 'chat.html', {'chatroom':chatroom, 'messages':messages})
