import pandas as pd
import numpy as np
import os
import statsmodels.api as sm
from django.shortcuts import render


# get all industries
def getindustry():
    df = pd.read_excel ('static/assets/dataset/RBIdataset.xlsx')
    # All industries available
    industry = df.Industry.unique() 
    return industry

# return dataframe,date,revenue data of given industry
def getindustrydata(name):
    df = pd.read_excel ('static/assets/dataset/RBIdataset.xlsx')
    # Getting data of industry
    selectedI = df[df.Industry == name]
    selectedI = selectedI.set_index('Period')
    rdate = (selectedI.index).strftime("%B %d, %Y")
    rdata = (selectedI[' Quarterly Revenues'])
    return selectedI,rdate,rdata

# get quarter data
def quarterdata(name):
    # Get quarter data
    ind,idate,idata = getindustrydata(name)
    qtrrev = ind[' Quarterly Revenues'].iloc[-1]
    qtrper = np.array(ind[' Quarterly Revenues'].tail(2))
    qtrper = ((qtrper[1] - qtrper[0])/qtrper[0])*100
    qtrper = "{:.2f}".format(qtrper)
    return qtrrev,qtrper

# get year data
def getyear(name):
    ind,idate,idata = getindustrydata(name)
    yrrev = np.array(ind[' Quarterly Revenues'].tail(4)).mean()
    s8 = np.array(ind[' Quarterly Revenues'].tail(8)).sum()
    s4 = np.array(ind[' Quarterly Revenues'].tail(4)).sum()
    sum2 = s8 - s4
    yrper = ((s4 - sum2)/sum2)*100
    yrper = "{:.2f}".format(yrper)
    return yrrev,yrper

# get date range
def getdaterange(name):
    GAV,gdate,gdata = getindustrydata(name)
    mindate = GAV.index.min().strftime("%B %d, %Y")
    maxdate = GAV.index.max().strftime("%B %d, %Y")
    return mindate,maxdate

# get all time mean and max min revenue value
def getatmandrange(name):
    GAV,gdate,gdata = getindustrydata(name)
    # All time mean
    atm = np.array(GAV[' Quarterly Revenues']).mean()
    atm = "{:.2f}".format(atm)
    # max and min value
    maxv = GAV[' Quarterly Revenues'].max()
    minv = GAV[' Quarterly Revenues'].min()
    minrev = GAV[' Quarterly Revenues'].min()
    maxrev = GAV[' Quarterly Revenues'].max()
    range = maxv - minv
    return atm,range

# get radar graph data:
def getradar(name):
    df = pd.read_excel ('static/assets/dataset/RBIdataset.xlsx')
    GAV,gdate,gdata = getindustrydata(name)
    rdate = GAV.index.max()
    radar = df[df.Period == rdate]
    ri = radar['Industry']
    ri = ri[:-1]
    rv = radar[' Quarterly Revenues']
    rv = rv[:-1]
    return ri,rv

# timeseries forecast model
def getmodelres(name):
    GAV,gdate,gdata = getindustrydata(name)
    # model train
    industry_ip = GAV[' Quarterly Revenues'].interpolate(method="linear")
    mod = sm.tsa.statespace.SARIMAX(industry_ip,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 1, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
    results = mod.fit()
    
    # Validating result
    pred = results.get_prediction(start=pd.to_datetime('2017-01-01'), dynamic=False)
    pred_ci = pred.conf_int()
    vdate = pred_ci.index
    vval = pred_ci.mean(axis =1)
    ax = GAV['2014':]
    axdate = ax.index
    axval = np.array(ax[' Quarterly Revenues'])

    # Forecast result
    prediction = results.get_forecast(steps=15)
    int_prediction = prediction.conf_int()
    fdate = int_prediction.index
    fval = int_prediction.mean(axis =1)
    return axdate,axval,vdate,vval,fdate,fval
        

# Create your views here.
def homePage(request):
    # All industries available
    industry = getindustry()
    if request.method == 'POST':
        selected = request.POST.get('selectedindustry')
    else:
        selected = 'Total Gross Value Added'

    # Getting data of GAV
    GAV,gdate,gdata = getindustrydata('Total Gross Value Added')
    # Agriculture 
    ag,agdate,agdata = getindustrydata('Agriculture, Forestry, Fishing')
    # mining
    m,mdate,mdata = getindustrydata('Mining & Quarying')
    # manufacturing
    ma,madate,madata = getindustrydata('Manufacturing')
    # essential utility
    eu,eudate,eudata = getindustrydata('Essential Utilities')
    # construction
    c,cdate,cdata = getindustrydata('Construction')
    #transport
    t,tdate,tdata = getindustrydata('Transport & Communication')
    #realestate
    r,rdate,rdata = getindustrydata('Real Estate and Financial Services')
    #defense
    d,ddate,ddata = getindustrydata('Defence Services ')

    # current industry data
    cur,date,data = getindustrydata(selected)

    # Get Date range
    mindate,maxdate = getdaterange(selected)

    # Get quarter data
    qtrrev,qtrper = quarterdata(selected)

    # Year Data
    yrrev,yrper = getyear(selected)

    # All time mean
    atm,range = getatmandrange(selected)

    # radar graph
    ri,rv = getradar(selected)

    # model result
    axdate,axval,vdate,vval,fdate,fval = getmodelres(selected)
    print(fdate)
    
    context = {
        'industry' : industry,
        'selected' : selected,
        'mindate' : mindate,
        'maxdate' : maxdate,
        'qtrrev' : qtrrev,
        'yrrev' : yrrev,
        'qtrper' : qtrper,
        'yrper' : yrper,
        'atm' : atm,
        'range' : range,
        'date' : date,
        'data' : data,
        'ri' : ri,
        'rv' : rv,
        'axdate' : axdate,
        'axval' : axval,
        'vdate' : vdate,
        'vval' : vval,
        'fdate' : fdate,
        'fval' : fval,
        'agdate' : agdate,
        'agdata' : agdata,
        'mdate' : mdate,
        'mdata' : mdata,
        'madate' : madate,
        'madata' : madata,
        'eudate' : eudate,
        'eudata' : eudata,
        'cdate' : cdate,
        'cdata' : cdata,
        'tdate' : tdate,
        'tdata' : tdata,
        'rdate' : rdate,
        'rdata' : rdata,
        'ddate' : ddate,
        'ddata' : ddata,
        'gdate' : gdate,
        'gdata' : gdata
    }
    return render(request,'index.html',context)
