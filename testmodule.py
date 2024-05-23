from bs4 import BeautifulSoup
import requests # sends requests to a website
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from pandas import DataFrame
from datetime import datetime

from selenium import webdriver
import chromedriver_autoinstaller

import re

import os
from pathlib import Path

today_ = datetime.today().strftime('%Y-%m-%d')

def webscrape_data():
    chromedriver_autoinstaller.install() 
    death_source = []

    base_url = 'https://www.realmeye.com/recent-deaths/'

    # Initialize an empty list to store website names
    website_names = ['https://www.realmeye.com/recent-deaths/']

    # Generate website names
    for i in range(101, 6000, 100):
        website_names.append(base_url + str(i))


    for i in range(len(website_names)):
        print(f'{int(i)}/77')
        driver = webdriver.Chrome()
        
        driver.maximize_window()
        driver.get(website_names[i])


        for i in range(1,101):
            element = driver.find_element_by_xpath(f"/html/body/div[1]/div/div/div[3]/table/tbody/tr[{i}]")
            death_source.append(element.text)

        driver.quit()
        
    df = pd.DataFrame(death_source)
    # print(len(df))

    df = df.rename(columns={0:"death_source"})   
    df = pd.DataFrame(death_source)
    # print(len(df))

    df = df.rename(columns={0:"death_source"})    

    df.replace('', pd.NA, inplace=True)
    df.dropna(inplace=True)

    columns1 = ['Player Name', 'Date', 'Time', 'Max Ratio', 'Cause of Death']
    column = []
    for j in range(len(df['death_source'])):
        parts = df['death_source'][j].split()
        for i in range(len(parts)):
            if '/8' in parts[i] :
                column.append(parts[:3]+ [parts[i]] + [' '.join(parts[i+1:])] )

    df = pd.DataFrame(column, columns = columns1)

    today = datetime.today().strftime('%Y-%m-%d')

    df.to_csv(f'./May 24/Daily files/{today}.csv')

def load_and_process(filename):
    df = pd.read_csv(filename)
    df.replace('', pd.NA, inplace=True)
    df.dropna(inplace=True)
    
    new_sum2 = pd.DataFrame(df.groupby('Max Ratio')['Cause of Death'])
    
    name_counts = pd.DataFrame(df['Player Name'].value_counts())
    
    counts = []
    causes = []
    count = []
    for i in range(len(new_sum2)):
        counts.append(new_sum2[1][i].value_counts())
        df_new = pd.DataFrame(counts[i])
        causes.append(df_new.index)
        count.append(df_new)


    causes = pd.DataFrame(causes); count = pd.DataFrame(count).dropna(axis=1, how= 'any')
    merge_again = pd.DataFrame(causes.values.tolist()).combine_first(pd.DataFrame(count.values.tolist())).dropna(axis=1, how= 'any')

    merge_again1 = merge_again[0][:]
    dicts = []
    for i in range(len(merge_again)):
        d_values = dict(zip(merge_again.T[i], count[0][i]['Cause of Death'][:38]))
        dicts.append(d_values)
        
    result = count_key_occurrences(dicts)
    final_dict = sort_by_highest_sum(result) 
    
    return result, final_dict, name_counts

def plot_stat_CD(result, final_dict):
    plt.figure(figsize = (30,5))
    plt.style.use('dark_background')
    cmap = plt.get_cmap('Reds')
    colors = [cmap(i / 9) for i in range(10)]
    today_ = datetime.today().strftime('%Y-%m-%d')
    for j in range(0,30):
        final_key, final_val = find_item_by_index(result, list(final_dict.values())[j])    
        bottom1 = 0
        color_count = 0
        for i in range(len(final_val)):
            if final_val[i] == 0 and i == 0:
                bottom1 = 0
                color_count += 1
            else:
                if i != 0:
                    bottom1 += final_val[i-1]
                elif i ==0:
                    bottom1 += 0
                color_count+=1
                plt.bar(final_key, final_val[i], bottom = bottom1, label = f'{i}/8', color = colors[color_count])
    plt.xticks(rotation = 90, size = 25)
    plt.yticks(rotation = 90, size = 15)
    plt.xlim(-1, 30 - 0.5)
    plt.savefig(f'./May 24/Daily photos/{today_}_daily', facecolor = 'Black', bbox_inches='tight')
    plt.show()
    
def rank_array(arr):
    # Enumerate the array to get (index, value) pairs
    indexed_arr = list(enumerate(arr))

    # Create a dictionary with the original values as keys and ranks as values
    rank_dict = {value: rank + 1 for rank, (index, value) in enumerate(indexed_arr)}

    return rank_dict

def count_key_occurrences(dicts_list):
    # Gather all unique keys across all dictionaries
    all_keys = set(key for dictionary in dicts_list for key in dictionary.keys())
    
    # Initialize the result dictionary with empty lists for all keys
    result = {key: [] for key in all_keys}

    # Iterate through each dictionary in the list
    for dictionary in dicts_list:
        # Iterate through all unique keys
        for key in all_keys:
            # Append the value if the key exists, otherwise append 0
            result[key].append(dictionary.get(key, 0))
    
    return result

def sort_by_highest_sum(result):
    # Calculate the sum of each list in the dictionary
    sums = {key: sum(values) for key, values in result.items()}
    
    # Sort keys by their sums in descending order
    sorted_keys = sorted(sums.keys(), key=lambda x: sums[x], reverse=True)
    
    # Keep track of the original location of each key
    original_locations = {key: list(result.keys()).index(key) for key in sorted_keys}
    
    # Initialize the final dictionary with order of highest sums
    final_dict = {sum_key: original_locations[sum_key] for sum_key in sorted_keys}
    
    return final_dict


def find_item_by_index(dictionary, index):
    try:
        key = list(dictionary.keys())[index]
        value = dictionary[key]
        return key, value
    except IndexError:
        return None
            
