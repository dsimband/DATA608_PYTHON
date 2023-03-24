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
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]



app = Dash(__name__,external_stylesheets=external_stylesheets)



def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table


def create_graph(graph_df):
    
    # g = sns.FacetGrid(graph_df,
    #             col='borough',
    #             sharex=False,
    #             sharey=False,
    #             height=4)
    # g = g.map(sns.barplot, 'value', 'tree species', "variable",
    #           hue_order=np.unique(graph_df["variable"]), 
    #           order=np.unique(graph_df["tree species"]), 
    #           errorbar=None,
    #           palette='dark')
    # g.add_legend()
    
    # plt.show()
    
    #return graph_df
    
    df = px.data.stocks()
    
    fig = go.Figure([go.Scatter(x = df['date'], y = df['GOOG'],
                     line = dict(color = 'firebrick', width = 4), name = 'Google')])
    fig.update_layout(title = 'Prices over time',
                      xaxis_title = 'Dates',
                      yaxis_title = 'Prices' )
    return fig


tree_df = pd.read_csv('trees_summary.csv')
tree_df['borocode'] = tree_df['borocode'].apply(str)
tree_df['spccode'] = tree_df['spccode'].apply(str)


br_df = tree_df[['borocode','borough']].drop_duplicates()
br_dict = br_df.to_dict('records') 

tn_df = tree_df[['spccode','tree species']].drop_duplicates()
tn_dict = tn_df.to_dict('records') 




initial_values_boro = [
    [{'value': i['borocode'],'label': i['borough']} for i in br_dict],
    [],
]


initial_values_trees = [
    [{'value': j['spccode'],'label': j['tree species']} for j in tn_dict],
    [],
]



app.layout = html.Div([
    
    
    html.Div([dmc.TransferList(
        id="transfer-list-boro", 
        value=initial_values_boro,
        nothingFound="Nothing Selected",
        listHeight = 140,
        transferAllMatchingFilter=True),]),       
    html.Div([dmc.TransferList(
        id="transfer-list-trees", 
        value=initial_values_trees,
        nothingFound="Nothing Selected",
        listHeight = 200,
        transferAllMatchingFilter=True),]),
    
    
    
    #html.Div(id='tree_graph'),    
    
    html.Div([dcc.Graph(id="tree_graph")]), 
    
    #html.Div([dcc.Graph(id = 'tree_graph', figure = create_graph(None)) ]),
          
    html.Div([
        html.Div([
            dmc.Table(
                id = 'tree_table',
                striped=True,
                highlightOnHover=True,
                withBorder=True,
                withColumnBorders=True,
        ),], style={'width': '100%', 'float': 'right', 'display': 'inline-block'}),
    ]), 
])





@app.callback(
    Output("tree_table", "children"),
    Output("tree_graph", "figure"),
    Input("transfer-list-boro", "value"),
    Input("transfer-list-trees", "value"),
)
def update_tree_table(boro_value, tree_value):
 
    b_df = pd.DataFrame(boro_value[1])
    b_df.rename({'value': 'borocode', 'label': 'borough'}, axis=1, inplace=True)
    boro_list2 = create_table(b_df)
    
    t_df = pd.DataFrame(tree_value[1])
    t_df.rename({'value': 'spccode', 'label': 'tree species'}, axis=1, inplace=True)
    tree_list2 = create_table(t_df)
   
    
    # no boro or tree type selected
    if not (b_df.empty or t_df.empty):
        treeSummary_df = tree_df[['borocode','borough','spccode','tree species','steward','count_health_good',
                                  'count_health_fair','count_health_poor','tree count','good','fair','poor']]
        treeSummary_df = pd.merge(treeSummary_df, b_df[['borocode']], how="right", on=["borocode"])
        treeSummary_df = pd.merge(treeSummary_df, t_df[['spccode']], how="right", on=["spccode"])
        table_df = treeSummary_df[['borough','tree species','steward','tree count','good','fair','poor']]
        table_df = round(table_df,4)
        tree_table = create_table(table_df)
        
        graph_df = treeSummary_df.groupby(['borough','tree species'])[['tree count','count_health_good',
                                                                       'count_health_fair','count_health_poor']].sum().reset_index()
        graph_df['good'] = round(graph_df['count_health_good'] / graph_df['tree count'] * 100,2)
        graph_df['fair'] = round(graph_df['count_health_fair'] / graph_df['tree count'] * 100,2)
        graph_df['poor'] = round(graph_df['count_health_poor'] / graph_df['tree count'] * 100,2)       
        graph_df = pd.melt(graph_df, id_vars=['borough','tree species'], value_vars=['good','fair','poor'])
        
        tree_fig = px.bar(graph_df, x='value', y='tree species',color="variable" ,facet_col="borough")
        #fig.show()
        
        return tree_table, tree_fig
    else:
        return None, None
    





if __name__ == '__main__':
    app.run_server(debug=True)
    
    