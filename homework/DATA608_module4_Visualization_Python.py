#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 22:07:54 2023

@author: dsimbandumwe
"""



from dash import Dash, dcc, Input, Output, html
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table


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



app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'DATA608 Module 4', style = {'textAlign':'center',
                                            'marginTop':20,'marginBottom':20,
                                            'marginLeft':20,'marginRight':20}),



        html.Div([dmc.TransferList(
            id="transfer-list-boro", 
            value=initial_values_boro,
            nothingFound="Nothing Selected",
            listHeight = 140,
            transferAllMatchingFilter=True),
            ],style = {'textAlign':'center','marginTop':10,'marginBottom':10}),       
        html.Div([dmc.TransferList(
            id="transfer-list-trees", 
            value=initial_values_trees,
            nothingFound="Nothing Selected",
            listHeight = 200,
            transferAllMatchingFilter=True),
            ],style = {'textAlign':'center','marginTop':10,'marginBottom':10}),   

        html.Div([dcc.Graph(id = 'bar_plot')] ,style = {'textAlign':'center','marginTop':10,'marginBottom':10}),   
        
        html.Div([
            dmc.Stack(
                children=[
                    dmc.Divider(variant="solid"),
                    dmc.Divider(variant="dashed"),
                    dmc.Divider(variant="dotted"),
                ],
            ),
        ]),
        
        html.Div([
            html.Div([
                dmc.Table(
                    id = 'tree_table',
                    striped=True,
                    highlightOnHover=True,
                    withBorder=False,
                    withColumnBorders=True,
            ),], style={'width': '95%', 'float': 'center', 'display': 'inline-block','textAlign':'center'}),
        ]),        
             
        
    ],style = {'textAlign':'center','marginTop':20,'marginBottom':20,'marginLeft':20,'marginRight':20,
              'font-size': 10,})
    
    

@app.callback(
    Output("tree_table", "children"),
    Output("bar_plot", "figure"),
    Input("transfer-list-boro", "value"),
    Input("transfer-list-trees", "value"),
)
def graph_update(boro_value, tree_value):
   
    
    b_df = pd.DataFrame(boro_value[1])
    b_df.rename({'value': 'borocode', 'label': 'borough'}, axis=1, inplace=True)
     
    t_df = pd.DataFrame(tree_value[1])
    t_df.rename({'value': 'spccode', 'label': 'tree species'}, axis=1, inplace=True)
    
    
    if not (b_df.empty or t_df.empty):
    
        treeSummary_df = tree_df[['borocode','borough','spccode','tree species','steward','count_health_good',
                                  'count_health_fair','count_health_poor','tree count','good','fair','poor']]
        treeSummary_df = pd.merge(treeSummary_df, b_df[['borocode']], how="right", on=["borocode"])
        treeSummary_df = pd.merge(treeSummary_df, t_df[['spccode']], how="right", on=["spccode"])        

            
        # data for table
        table_df = treeSummary_df[['borough','tree species','steward','tree count','good','fair','poor']]
        table_df = round(table_df,4)
        tree_table = create_table(table_df)



        # data for graph
        graph_df = treeSummary_df.groupby(['borough','tree species'])[['tree count','count_health_good',
                                                                       'count_health_fair','count_health_poor']].sum().reset_index()
                
        graph_df['good'] = round(graph_df['count_health_good'] / graph_df['tree count'] * 100,2)
        graph_df['fair'] = round(graph_df['count_health_fair'] / graph_df['tree count'] * 100,2)
        graph_df['poor'] = round(graph_df['count_health_poor'] / graph_df['tree count'] * 100,2)
        
        graph_df = pd.melt(graph_df, id_vars=['borough','tree species'], value_vars=['good','fair','poor'])
 
        
        graph_df = treeSummary_df
        graph_df = pd.melt(graph_df, id_vars=['borough','tree species','steward'], value_vars=['good','fair','poor'])
        fig = px.bar(graph_df, x='value', y='tree species',color="variable" ,facet_col="borough", facet_row='steward',
                    height=800, color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(template="simple_white", title="Tree Health")
        
        return tree_table, fig
    
    else:
        fig = px.bar()
        fig.update_layout(template="simple_white", title="Tree Health")
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return None, fig
    



if __name__ == '__main__': 
    app.run_server()
    
    
    
    
    
    
    
    
    
    