# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 10:46:59 2021

@author: adamm
"""

"""
A practice project looking at changes in NOx measurements in Bristol St Pauls over the last 15 years
"""

"""
1 - combine the three files into one pandas dataframe
"""

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt 

path = os.path.dirname(__file__)
files = glob.glob(path + '\Bristol NOx*.csv')

dataFiles = []
for filename in files:
    data = pd.read_csv(filename, header=4, skipfooter=4) #column names are on row 5, so set header=4 (starts at 0), also skip the last 4 lines, as these are blank and just contain the word 'End'
    dataFiles.append(data)

nox = pd.concat(dataFiles, ignore_index=True) # join the files together, ignore_index sets a new index, there were problems with the index resetting for each file

print(files)

print(nox.columns) #Show columns are correct

# print(nox.dtypes) #Show data types for each column

# print(nox.head(20)) #Inspect first 20 rows of data


"""
2 - Tidy data to improve usability
    Decide what to do with missing data
    Change status column so it just contains the units (ugm-3 = micrograms per metre cubed)
    Change data types in Date, Time and Nitrogen Oxides columns
    Change 'Nitrogen oxides as nitrogen dioxide' column name to 'Nitrogen_Oxides'
"""

nox = nox.rename(columns = {'Nitrogen oxides as nitrogen dioxide': 'Nitrogen_Oxides'}) #Rename 'Nitrogen oxides as nitrogen dioxide' to 'Nitrogen_Oxides'

nox.Status = nox['Status'].replace('\w\s', '', regex=True) #Remove initial letter and space from start of Status column


#Split Date and Time in to day, month, year and hour, so that analysis can be carried out by day, month, year, or hour

nox['Day'] = nox['Date'].str[0:2]
nox['Month'] = nox['Date'].str[3:5]
nox['Year'] = nox['Date'].str[6:]
nox['Hour'] = nox['Time'].str[0:2]


#Set Day, Month, Year, and Hour data types to numeric

nox['Day'] = pd.to_numeric(nox.Day)
nox['Month'] = pd.to_numeric(nox.Month)
nox['Year'] = pd.to_numeric(nox.Year)
nox['Hour'] = pd.to_numeric(nox.Hour)



#Convert Nitrogen_oxides to numeric, setting any 'No data' to NaN - this is so any missing values are ignored (errors = 'coerce')

nox['Nitrogen_Oxides'] = pd.to_numeric(nox.Nitrogen_Oxides, errors='coerce')


print(nox.dtypes) #Show data types for each column

print(nox.head(20)) #Inspect first 20 rows of data


"""
3 - Plot raw data
"""

# fig,ax = plt.subplots()
# ax.plot(nox.Date, nox.Nitrogen_Oxides)
# ax.set(xlabel='Date', ylabel = 'NOx ugm-3')
# plt.show()


"""
4 - Analyse data
    NOx must not exceed 200 ugm-3 no more than 18 times each year, averaged every hour
    NOx must not exceed 40 ugm-3 averaged over one year
"""

# Create a list of each year, used to iterate across the dataset

yearList = []
for year in nox.Year:
    if year in yearList:
        continue
    else:
        yearList.append(year)
        
        
# Find average, maximum, minimum NOx values for each year, also number of measurements exceeding 200 ugm-3 for each year      


yearlyAverageNox = []
yearlyMaxNox = []
yearlyMinNox = []
yearlyCountOver200 = []
for year in yearList:
    df = nox[nox.Year == year]
    yearlyAverageNox.append(df.Nitrogen_Oxides.mean())
    yearlyMaxNox.append(df.Nitrogen_Oxides.max())
    yearlyMinNox.append(df.Nitrogen_Oxides.min())
    over200Counter = 0
    for value in df.Nitrogen_Oxides:
        if value >= 200:
            over200Counter += 1
    yearlyCountOver200.append(over200Counter)
    


# Find monthly average NOx values

monthList = list(range(1, 13, 1)) # Create a 'month list', it's just a list from 1 - 12 to iterate over

monthlyAverageNox = []
monthlyMaxNox = []
monthlyMinNox = []
for year in yearList:
    for month in monthList:
        df = nox[(nox.Year == year) & (nox.Month == month)]
        monthlyAverageNox.append(df.Nitrogen_Oxides.mean())
        monthlyMaxNox.append(df.Nitrogen_Oxides.max())
        monthlyMinNox.append(df.Nitrogen_Oxides.min())
        

# Find daily average NOx values - This is more difficult because of leap years
        
dayList = list(range(1, 31, 1)) # Create a 'day list' from 1 - 31, used to iterate over

dailyAverageNox = []
dailyMaxNox = []
dailyMinNox = []
for year in yearList:
    for month in monthList:
        for day in dayList:
            df = nox[(nox.Year == year) & (nox.Month == month) & (nox.Day == day)]
            dailyAverageNox.append(df.Nitrogen_Oxides.mean())
            dailyMaxNox.append(df.Nitrogen_Oxides.max())
            dailyMinNox.append(df.Nitrogen_Oxides.min())




    
"""
5 - Plot data
"""


# Plot yearly average data

fig, ax = plt.subplots()
ax.bar(yearList, yearlyAverageNox)
ax.set(xlabel='Year', ylabel='NOx ugm-3', title='Average Annual Nox')
plt.hlines(40, yearList[0] -1, yearList[-1] +1, colors='r', linestyles='dashed')



# Plot monthly average data

fig, ax = plt.subplots()
ax.bar(list(range(1,len(monthlyAverageNox) +1)), monthlyAverageNox)
ax.set(xlabel='Month', ylabel='NOx ugm-3', title='Average Monthly Nox')



# Plot daily average data

fig, ax = plt.subplots()
ax.bar(list(range(1,len(dailyAverageNox) +1)), dailyAverageNox)
ax.set(xlabel='Day', ylabel='NOx ugm-3', title='Average Daily Nox')



#  Plot number of measurements exceeding 200 ugm-3 for each year 

fig, ax = plt.subplots()
ax.bar(yearList, yearlyCountOver200)
ax.set(xlabel='year', ylabel='Number', title='Number of Measurements Over 200 ugm-3')
plt.hlines(18, yearList[0] -1, yearList[-1] +1, colors='r', linestyles='dashed')
plt.show()


