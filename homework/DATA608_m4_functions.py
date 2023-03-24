#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 22:07:54 2023

@author: dsimbandumwe
"""

import pandas as pd
import numpy as np


def process_tree_data():
  boro_set = {1,2,3,4,5}
  tree_df = pd.DataFrame()


  for i in boro_set:
      
      soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=100000&$offset=0' +\
              '&$select=borocode,boroname,spc_common,steward,count(tree_id),' +\
              'COUNT(CASE WHEN health=\'Good\' THEN 1 END) AS count_health_good,'     +\
              'COUNT(CASE WHEN health=\'Fair\' THEN 1 END) AS count_health_fair,'     +\
              'COUNT(CASE WHEN health=\'Poor\' THEN 1 END) AS count_health_poor'     +\
              '&$where=borocode='+ str(i) +\
              '&$group=borocode,boroname,spc_common,steward').replace(' ', '%20')
      df = pd.read_json(soql_url)
      
      df['good'] = round(df['count_health_good'] / df['count_tree_id'] * 100,2)
      df['fair'] = round(df['count_health_fair'] / df['count_tree_id'] * 100,2)
      df['poor'] = round(df['count_health_poor'] / df['count_tree_id'] * 100,2)

      tree_df =  pd.concat([tree_df, df], ignore_index=True)
     
        
  tree_df = tree_df.replace(np.nan, 'Unknown', regex=True)
  tree_df = tree_df.rename(columns={"count_tree_id": "tree count"})
  tree_df = tree_df.rename(columns={"spc_common": "tree species"})
  tree_df = tree_df.rename(columns={"boroname": "borough"})
  
  
    
  tn_df = tree_df[['tree species']].drop_duplicates().reset_index()
  tn_df = tn_df.rename(columns={"index": "spccode"})
  tn_df['spccode'] = tn_df.index   

  tree_df =  pd.merge(tree_df, tn_df, how="outer", on=["tree species"])

   
  tree_df.to_csv('trees_summary.csv', index=False)
      
      
      
      
if __name__ == "__main__":
    process_tree_data()