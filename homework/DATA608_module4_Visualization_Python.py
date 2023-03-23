#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 21:57:27 2023

@author: davidsimbandumwe
"""


from dash import Dash, dcc, html, Input, Output, dash_table
import dash_mantine_components as dmc
import pandas as pd
import numpy as np



app = Dash(__name__)



def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table






tree_df = pd.read_csv('trees_summary.csv')
tree_df['borocode'] = tree_df['borocode'].apply(str)
tree_df['spccode'] = tree_df['spccode'].apply(str)


br_df = tree_df[['borocode','boroname']].drop_duplicates()
br_dict = br_df.to_dict('records') 

tn_df = tree_df[['spccode','spc_common']].drop_duplicates()
tn_dict = tn_df.to_dict('records') 




initial_values_boro = [
    [{'value': i['borocode'],'label': i['boroname']} for i in br_dict],
    [],
]


initial_values_trees = [
    [{'value': j['spccode'],'label': j['spc_common']} for j in tn_dict],
    [],
]



app.layout = html.Div([
    
    

    
    html.Div([dmc.TransferList(id="transfer-list-boro", value=initial_values_boro),]),       
    html.Div([dmc.TransferList(id="transfer-list-trees", value=initial_values_trees),]),
          

   html.Div([    
    
                html.Div([
                    dmc.Table(
                        id = 'boro_list2',
                        striped=True,
                        highlightOnHover=True,
                        withBorder=True,
                        withColumnBorders=True,
                    ), 
                  ], style={'width': '20%', 'display': 'inline-block'}),  
                html.Div([  
                    dmc.Table(
                        id = 'tree_list2',
                        striped=True,
                        highlightOnHover=True,
                        withBorder=True,
                        withColumnBorders=True,
                    ),
                ], style={'width': '20%', 'float': 'right', 'display': 'inline-block'}),
    
            ]),     
    
    html.Div([
        dmc.Table(
            id = 'tree_table',
            striped=True,
            highlightOnHover=True,
            withBorder=True,
            withColumnBorders=True,
        ),
        ]),
    
    
    
])





@app.callback(
    Output("boro_list2", "children"),
    Output("tree_list2", "children"),
    Output("tree_table", "children"),
    Input("transfer-list-boro", "value"),
    Input("transfer-list-trees", "value"),
)
def update_tree_table(boro_value, tree_value):
 
    b_df = pd.DataFrame(boro_value[1])
    b_df.rename({'value': 'borocode', 'label': 'boroname'}, axis=1, inplace=True)
    boro_list2 = create_table(b_df)
    
    t_df = pd.DataFrame(tree_value[1])
    t_df.rename({'value': 'spccode', 'label': 'spc_common'}, axis=1, inplace=True)
    tree_list2 = create_table(t_df)

    
    
    # no boro or tree type selected
    if not (b_df.empty or t_df.empty):
        treeSummary_df = tree_df[['borocode','boroname','spccode','spc_common','steward','per_good','per_fair','per_poor']]
        treeSummary_df = pd.merge(treeSummary_df, b_df[['borocode']], how="right", on=["borocode"])
        treeSummary_df = pd.merge(treeSummary_df, t_df[['spccode']], how="right", on=["spccode"])
        tree_table = create_table(treeSummary_df)
        
        return boro_list2, tree_list2, tree_table
    else:
        return boro_list2, tree_list2, None
    





if __name__ == '__main__':
    app.run_server(debug=True)
    
    