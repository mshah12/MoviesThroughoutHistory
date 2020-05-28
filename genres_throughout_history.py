# -*- coding: utf-8 -*-
"""Genres_Throughout_History (FINAL).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/116wncKtMbsk8qqTN3y-ytHpTc711LuaA
"""

import requests
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
#please follow instructions on https://developers.themoviedb.org/3/getting-started/introduction to generate your own api_key
api_key = '0b00aa2f6634799ce335997d073174e6' #replace string with your generated key

def getMovies(startYear, endYear, country, languages): #query and pull up to 20 results at a time, this application only does page 1 (so top 20)
  films = {}
  yearly_set = []
  for year in range(startYear, endYear + 1):
   # print(year)
    if(len(languages) > 1): #case where a country has more than one official language
    #  print("Multilingual Nation")
      ml_set = {}
      ml_set_2 = {}
      for subyear in range(startYear, endYear + 1):
        ml_set[subyear] = []  
      for lang_key in languages:
        #print(lang_key)
        reponse = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + api_key + '&sort_by=popularity.desc' + '&with_original_language=' + lang_key + '&primary_release_year=' + str(year) + '&region=' + country + '&year=' + str(year)) #makes a request based on the year
        movies = reponse.json()
        movies_in_year = movies['results'] #results is the only relevant data from the return
        if(len(movies_in_year) > 0):
          ml_set_2[lang_key] = (movies_in_year)
          yearly_set.append(movies_in_year)
          # print(yearly_set)
          # print(ml_set[lang_key])
      #     #films[year] = movies_in_year  
      for value in ml_set_2.values():
        ml_set[year].append(value)
      films[year] = ml_set[year]
    else:
     # print("Monolingual Nation")
      lang_key = languages[0]
      reponse = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + api_key + '&sort_by=popularity.desc' + '&with_original_language=' + lang_key + '&primary_release_year=' + str(year) + '&region=' + country + '&year=' + str(year)) #makes a request based on the year
      movies = reponse.json()
      movies_in_year = movies['results'] #results is the only relevant data from the return
      yearly_set.append(movies_in_year)
 #     print(yearly_set)
      films[year] = yearly_set[len(yearly_set)-1] #works only for nations with one official language
      yearly_set.clear()
    #print(films[year])
  return films

def buildYearlyDataset(films, languages):
  dataset = {}
  for year in films:
    print("Year: " + str(year))
    for film in films[year]:
      if(len(languages) > 1):
        for language_specific_film in film: #multilingual countries
          film_obj = requests.get('https://api.themoviedb.org/3/movie/'+ str(language_specific_film['id']) +'?api_key='+ api_key)
          film_obj = film_obj.json()
          print(str(language_specific_film['title']) + ", language: " + str(language_specific_film['original_language'])) #used for debugging
          dataset[str(language_specific_film['title'])] = language_specific_film['genre_ids']
      else:
        film_obj = requests.get('https://api.themoviedb.org/3/movie/'+ str(film['id']) +'?api_key='+ api_key)
        film_obj = film_obj.json()
        print(str(film['title']) + ", language: " + str(film['original_language'])) #used for debugging
        dataset[str(film['title'])] = (year, tuple(film['genre_ids']))
    print("")
  return dataset #returns a dictionary of {Title: (Year, Genre_ID)} 

def buildCountryDataSet(startYear, endYear, country_list, country_language_keys): 
  countries = {}
  for c in country_list:
    movie_api_response = getMovies(startYear, endYear, c, country_language_keys[c])
    temp = country_list.copy()
    print(temp.pop() + ': ')
    print('')
    movies = buildYearlyDataset(movie_api_response, country_language_keys[c])
    countries[c] = movies
  return countries #returns a dictionary of {Country: (Title: (Year, Genre_ID))}

def convertGenres(country_dataset):
  genre_obj = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=0b00aa2f6634799ce335997d073174e6&language=en-US")
  genre_obj = genre_obj.json()
  genres = {}
  genresDscrip = {}
  count = 0
  multiLang = 0
  for key in country_dataset.keys():
    if(key == "IN"):
      multiLang = 1
  for genre_type in genre_obj.values():
    for genre_ID in genre_type:
      for ID in (genre_ID.values()):
        if(count == 1):
          count = 0
          genresDscrip[ID] = 0
          continue
        genres[ID] = 0
        count += 1
  for movie in country_dataset.values():
    for data in movie.values():
      if(multiLang == 1): #if multilingual film, use different method
        for genre in data:
          genres[genre] += 1
      else: #else if monoligual, use normal method
        movieGenres = data[1]
        for genre in movieGenres:
          genres[genre] += 1
    i = 0;
    j = 0;
    for key in genresDscrip:
      for value in genres.values():
        if(i - j == 0):
          genresDscrip[key] = value
        j += 1
      j = 0
      i += 1
  return genresDscrip #returns a dictionary of {Genre: Number of films} 

def convertPercentage(num_films):
  sum = 0;
  total_num_films = num_films.values()
  for film in total_num_films:
    sum += film
  for key in num_films.keys():
    num_films[key] = (num_films[key] / sum)
  return num_films

"""
Supported Country IDs in ISO_3166-2 format: https://en.wikipedia.org/wiki/ISO_3166-2
Supported Language IDs in ISO_639-1 format: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes 
Add more to the keys of country codes and their language if you want to
For multilingual countries, default is all official languages (if narrower filter, better runtime)
"""
def pipeline(startYear, endYear, firstCountry, secondCountry):
  genres = {}
  country_and_languages = {
                           'CN' : ['zh'], # China
                           'DE' : ['de'], # Germany
                           'FR' : ['fr'], # France
                           'GB' : ['en'], # U.K
                           'IN' : ['hi', 'bn', 'ur', 'pa', 'mr', 'te', 'ta', 'gu', 'kn', 'or', 'ml', 'sa'], #India
                           'JP' : ['ja'], # Japan
                           'KR' : ['ko'], # Korea
                           'RU' : ['ru'], # Russia
                           'US' : ['en']  # United States of America
                           }
 # movie_set = getMovies(startYear, endYear, 'US', country_and_languages['US'])
  #yearly_set = buildYearlyDataset(movie_set, country_and_languages['US'])
  country_dataset1 = buildCountryDataSet(startYear, endYear, firstCountry, country_and_languages)
  genres1 = convertGenres(country_dataset1)
  country_dataset2 = buildCountryDataSet(startYear, endYear, secondCountry, country_and_languages)
  genres2 = convertGenres(country_dataset2)
  createPlot(firstCountry, secondCountry, startYear, endYear, convertPercentage(genres1), convertPercentage(genres2))

def createPlot(country1, country2, year1, year2, filmPercentage1, filmPercentage2):
  n_groups = 19
  means_c1 = (filmPercentage1['Action'] * 100, filmPercentage1['Adventure'] * 100, filmPercentage1['Animation'] * 100, filmPercentage1['Comedy'] * 100, filmPercentage1['Crime'] * 100, filmPercentage1['Documentary'] * 100, filmPercentage1['Drama'] * 100, filmPercentage1['Family'] * 100, filmPercentage1['Fantasy'] * 100, filmPercentage1['History'] * 100, filmPercentage1['Horror'] * 100, filmPercentage1['Music'] * 100, filmPercentage1['Mystery'] * 100, filmPercentage1['Romance'] * 100, filmPercentage1['Science Fiction'] * 100, filmPercentage1['TV Movie'] * 100, filmPercentage1['Thriller'] * 100, filmPercentage1['War'] * 100, filmPercentage1['Western'] * 100)
  means_c2 = (filmPercentage2['Action'] * 100, filmPercentage2['Adventure'] * 100, filmPercentage2['Animation'] * 100, filmPercentage2['Comedy'] * 100, filmPercentage2['Crime'] * 100, filmPercentage2['Documentary'] * 100, filmPercentage2['Drama'] * 100, filmPercentage2['Family'] * 100, filmPercentage2['Fantasy'] * 100, filmPercentage2['History'] * 100, filmPercentage2['Horror'] * 100, filmPercentage2['Music'] * 100, filmPercentage2['Mystery'] * 100, filmPercentage2['Romance'] * 100, filmPercentage2['Science Fiction'] * 100, filmPercentage2['TV Movie'] * 100, filmPercentage2['Thriller'] * 100, filmPercentage2['War'] * 100, filmPercentage2['Western'] * 100)

  c1 = country1.pop()
  c2 = country2.pop()

  # create plot
  fig, ax = plt.subplots()
  #fig.set_size_inches(100,20)
  index = np.arange(n_groups)
  bar_width = 0.35
  opacity = 0.8

  rects1 = plt.bar(index, means_c1, bar_width,
  alpha=opacity,
  color='b',
  label= c1)

  rects2 = plt.bar(index + bar_width, means_c2, bar_width,
  alpha=opacity,
  color='r',
  label= c2)

  plt.xlabel('Genres')
  plt.ylabel('Total Percentage of Films')
  plt.title('Comparison of Genres between ' + c1 + ' and ' + c2 + ' during ' + str(year1) +'-' + str(year2))
  plt.xticks(index + bar_width, ('Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'))
  plt.yticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
  plt.legend()

  plt.margins(x=0)
  plt.autoscale(True, 'x', True)
  #plt.tight_layout()
  ax.xaxis_date()     # interpret the x-axis values as dates
  fig.autofmt_xdate()
  plt.show()

startYear = int(input("Enter start year: "))
while(startYear > 2020):
  startYear = int(input("Invalid year. Re-enter start year: "))

endYear = int(input("Enter end year: "))
while(endYear > 2020):
  endYear = int(input("Invalid year. Re-enter end year: "))
while(endYear < startYear):
  endYear = int(input("End year cannot be less than start year. Re-enter end year: "))

countries = ['CN', 'DE', 'FR', 'GB', 'IN', 'JP', 'KR', 'RU', 'US']
for country in countries:
  print(country)
print("")
country1 = input("Please select a country from the list above: ")
while(country1 not in countries):
  country1 = input("Invalid country. Re-enter country from list: ")

country2 = input("Please select a second country from the list above: ")
while(country2 not in countries):
  country2 = input("Invalid country. Re-enter country from list: ")

print("")

pipeline(startYear, endYear, {country1}, {country2})

