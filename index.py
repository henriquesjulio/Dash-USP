from dash import html, dcc
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd

from app import *

import numpy as np
import plotly.express as px 
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from menu_styles import *

# Carregamento de dados

df = pd.read_csv('database/datawarehouse/Orcamento.csv')
df = df.drop(['Unnamed: 0'],axis=1)
df_coord = pd.read_csv('database/datawarehouse/Coordenadas.csv')
df_coord = df_coord.drop(['Unnamed: 0'],axis=1)
df = pd.merge(df, df_coord, how = 'outer', on = 'Unidade de Despesa')
df_store = df.to_dict()

# =========  Layout  =========== #

app.layout = dbc.Container([
                
                dcc.Store(id='dataset', data=df_store),
                dcc.Location(id='url', refresh=False),
                
                # Layout
                
                # Parte de cima do Dashboad
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([html.Img(src='assets/usp.png', height="150px"), "  Universidade de São Paulo"], className='textoSecundario'),
                                    dbc.Col([dbc.NavbarSimple(children=[
                                                            dbc.NavItem(dbc.NavLink("Mapa", href="/mapa")),
                                                            dbc.NavItem(dbc.NavLink("Evolução", href="/evolucao")),
                                                            dbc.NavItem(dbc.NavLink("Diferença", href="/diferenca")),
                                                            ], style={'align': 'right', 'width':'100px'},color = '#64c4d2', className='textoSecundario'
                                                            )
                                            ])
                                    ])
                        ])
                            ],className='card1_linha1')
                        ], xs=12, md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Legend('Unidade:', className='textoSecundario')
                                ], md=4, xs=3, style={'text-align': 'right'}),
                                    dbc.Col([
                                        dcc.Dropdown(
                                            id = 'select_unidade',
                                            value = 1,
                                            clearable = False,
                                            options =[ {'label': 'Todos', 'value': 1} ] + [ { 'label' : x , 'value' : x } for x in df['Unidade de Despesa'].sort_values(ascending=True).unique() ],
                                            style = {'color':'white'})
                                ], md=8, xs=6, style={'text-align': 'left'}),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('ANO: ', className='textoSecundario')
                                ], md=4, xs=3, style={'text-align': 'right'}),
                                dbc.Col([
                                    dcc.Dropdown(
                                        id = 'select_ano',
                                        value = 1,
                                        clearable = False,
                                        options = [ {'label': 'Todos', 'value': 1}] + [ {'label': x, 'value': x} for x in df.Ano.sort_values(ascending=False).unique()],
                                        multi= False,
                                        className='textoQuartenarioBranco'), 
                                    ], md=2, xs=6, style={'text-align': 'left'}),
                            ])
                        ])
                    ],className='card2_linha1')
                ], md=6, xs=12)
            ],  className='g-2 my-auto'),
                
                # Parte dos Indicadores
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([                                                
                                     ],md=12, id='cards_ativos'),
                            ],  className='g-2 my-auto')
                        ], xs=12, md=12),
                    ],  className='g-2 my-auto'),
                    
                # Parte dos Gráficos
                dbc.Row([
                    dbc.Col([
                            ], md=12, id = 'graphs_ativos')
                    ],  className='g-2 my-auto'),
                             
                ], fluid=True)

# Callback do Dashboard

@app.callback([
    Output('graphs_ativos' , 'children' ),
    Output('cards_ativos', 'children'),
    ],
    [
    Input( 'dataset' , 'data' ),
    Input( 'select_unidade', 'value' ),
    Input( 'select_ano' , 'value' ),
    Input( 'url', 'pathname')
    ])

def graph(data, unidade, ano, pathname):
    
    dff = pd.DataFrame(data)
    
    # Filtros do dados
    
    if (unidade == 1) & (ano == 1):
        dff = dff
    elif unidade == 1:
        dff = dff[dff['Ano'].isin([ano])]
    elif ano == 1:
        dff = dff[dff['Unidade de Despesa'].isin([unidade])]
        
    # Página da Evolução Orçamentária
    
    if pathname == '/evolucao':
        
        df_filtered = dff.groupby('Ano')[['Dotação Inicial (R$)', 'Dotação Atual (R$)','Empenhado (R$)','Liquidado (R$)','Pago (R$)']].sum().reset_index()
        
        df_dot = df_filtered[['Ano','Dotação Inicial (R$)','Dotação Atual (R$)']]
        
        # Primeiro Gráfico
        
        dotacao_figure = go.Figure(go.Bar(x = df_dot['Ano'],
                                          y= df_dot['Dotação Inicial (R$)'],
                                          name = 'Inicial (R$)',
                                          opacity = .8,
                                          marker_color=LISTA_DE_CORES_LINHAS[5],
                                          )
                                   )
            
        dotacao_figure.add_bar(x = df_dot['Ano'],
                               y = df_dot['Dotação Atual (R$)'],
                               name = 'Atual (R$)',
                               opacity = .8,
                               marker_color=LISTA_DE_CORES_LINHAS[1])   
        
        dotacao_figure.update_layout(title='Evolução Orçamentária por Dotação (Inicial, Atual)')
        dotacao_figure.update_xaxes(tickvals = df_dot['Ano'].unique())
        dotacao_figure.update_layout(MAIN_CONFIG, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
        dotacao_figure.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
        dotacao_figure.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
        
        
        # Segundo Gráfico
        
        df_graph = df_filtered[['Ano','Empenhado (R$)', 'Liquidado (R$)', 'Pago (R$)']]
        
        graph_figure = go.Figure(go.Bar(x = df_graph['Ano'],
                                        y = df_graph['Empenhado (R$)'],
                                        name = 'Empenhado (R$)',
                                        opacity = .8,
                                        marker_color=LISTA_DE_CORES_LINHAS[5])
                                 )
        graph_figure.add_scatter(x = df_graph['Ano'],
                                 y = df_graph['Liquidado (R$)'],
                                 name = 'Liquidado (R$)',
                                 line=dict(color=LISTA_DE_CORES_LINHAS[0], width= 4),
                                 )
        graph_figure.add_scatter(x = df_graph['Ano'],
                              y = df_graph['Pago (R$)'],
                              name = 'Pago (R$)', 
                              line=dict(color=LISTA_DE_CORES_LINHAS[1], width= 4),
                              )
        
        graph_figure.update_layout(title='Evolução Orçamentária (Empenhado, Liquidado, Pago)')
        graph_figure.update_xaxes(tickvals = df_filtered['Ano'].unique())
        graph_figure.update_layout(MAIN_CONFIG, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
        graph_figure.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
        graph_figure.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
        
        
        lista_linhas = []
        
        row = dbc.Row([
                    dcc.Graph(figure = dotacao_figure ,
                              config={"displayModeBar": False, "showTips": False},
                              className='graph_line',
                              id='dotacao_graph'
                              )
                      ]
                     )
        lista_linhas.append(row)
        
        row = dbc.Row([
                      dcc.Graph(figure = graph_figure,
                      config={"displayModeBar": False, "showTips": False},
                      className='graph_line',
                      id='eficiencia_graph'
                                )
                      ]
                     )
        lista_linhas.append(row)
        
        graph_ativos = dbc.Col([
            *lista_linhas
            ], id='graph_ativos')
        
        # Indicadores
        
        lista_colunas = []
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Empenhado/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Empenhado (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Empenhado', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Empenhado (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Dotação Atual em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Dotação Atual (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Empenhado em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Empenhado (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Pago (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
    
        
        card_ativos= dbc.Row([
            *lista_colunas
            ])
     
        
        return [graph_ativos, card_ativos]
    
    # Página da Diferença
    
    elif pathname == '/diferenca':
        
        df_filtered = dff.groupby('Ano')[['Dotação Inicial (R$)', 'Dotação Atual (R$)','Empenhado (R$)','Liquidado (R$)','Pago (R$)']].sum().reset_index()
        
        # Primeiro Gráfico
        
        dotacao_figure = go.Figure(go.Bar(x = df_filtered['Ano'],
                                          y= df_filtered['Dotação Atual (R$)'],
                                          name = 'Dotação Atual (R$)',
                                          opacity = .8,
                                          marker_color=LISTA_DE_CORES_LINHAS[5],
                                          )
                                   )
        
        dotacao_figure.add_bar(x = df_filtered['Ano'],
                               y = df_filtered['Empenhado (R$)'],
                               name = 'Empenhado (R$)',
                               opacity = .8,
                               marker_color=LISTA_DE_CORES_LINHAS[1])
        
        dotacao_figure.add_bar(x = df_filtered['Ano'],
                               y = df_filtered['Pago (R$)'],
                               name = 'Pago (R$)',
                               opacity = .8,
                               marker_color=LISTA_DE_CORES_LINHAS[0])
    
        dotacao_figure.update_layout(title='Soma Orçamentária (Dotação Atual, Empenhado, Pago)')
        dotacao_figure.update_xaxes(tickvals = df_filtered['Ano'].unique())
        dotacao_figure.update_layout(MAIN_CONFIG, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
        dotacao_figure.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
        dotacao_figure.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
        
        # Segundo Gráfico
        
        graph_figure = go.Figure(go.Scatter(x = df_filtered['Ano'],
                                            y = df_filtered['Empenhado (R$)'] - df_filtered['Dotação Atual (R$)'],
                                            name = 'Diferença Empenhado (R$)',
                                            opacity = .8,
                                            marker_color=LISTA_DE_CORES_LINHAS[5])
                                )
        
        graph_figure.add_scatter(x = df_filtered['Ano'],
                                 y = df_filtered['Pago (R$)'] - df_filtered['Dotação Atual (R$)'],
                                 name = 'Diferença Pago (R$)',
                                 line=dict(color=LISTA_DE_CORES_LINHAS[1], width= 4),
                                )
        
        graph_figure.update_layout(title='Diferença Orçamentária por Dotação Atual (Empenhado, Pago)')
        graph_figure.update_xaxes(tickvals = df_filtered['Ano'].unique())
        graph_figure.update_layout(MAIN_CONFIG, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
        graph_figure.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
        graph_figure.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
        
        lista_linhas = []
        
        row = dbc.Row([
                    dcc.Graph(figure = dotacao_figure ,
                              config={"displayModeBar": False, "showTips": False},
                              className='graph_line',
                              id='dotacao_graph'
                              )
                      ]
                     )
        lista_linhas.append(row)
        
        row = dbc.Row([
                      dcc.Graph(figure = graph_figure,
                      config={"displayModeBar": False, "showTips": False},
                      className='graph_line',
                      id='eficiencia_graph'
                                )
                      ]
                     )
        lista_linhas.append(row)
        
        graph_ativos = dbc.Col([
            *lista_linhas
            ], id='graph_ativos')
            
        
        
        # Indicadores
        
        lista_colunas = []
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Empenhado/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Empenhado (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Empenhado', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Empenhado (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
            dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('(Empenhado - Dotação Atual) em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format(((np.sum(df_filtered['Empenhado (R$)']) - np.sum(df_filtered['Dotação Atual (R$)']))/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('(Pago - Dotação Atual) em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format(((np.sum(df_filtered['Pago (R$)']) - np.sum(df_filtered['Dotação Atual (R$)']))/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('(Pago - Empenhado) em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format(((np.sum(df_filtered['Pago (R$)']) - np.sum(df_filtered['Empenhado (R$)']))/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        card_ativos= dbc.Row([
            *lista_colunas
            ])
     
        return [graph_ativos, card_ativos]
        
    # Página Principal e do Mapa
       
    else:
        
        df_filtered = dff.groupby('Ano')[['Dotação Inicial (R$)', 'Dotação Atual (R$)','Empenhado (R$)','Liquidado (R$)','Pago (R$)',]].sum().reset_index()
        
        dff_coord = dff.groupby(['Unidade de Despesa','lat','lng'])[['Dotação Atual (R$)','Pago (R$)']].sum().reset_index()
        
        mapbox_token = 'pk.eyJ1IjoiaGVucmlxdWVqdWxpbyIsImEiOiJjbHA4dGVtZHMyNXVkMnFucjg1eXpnanN6In0.U-7X1Kd-3Hh9Mgx_re8CUw'
        
        map_graph = px.scatter_mapbox(dff_coord,
                                      lat = dff_coord['lat'],
                                      lon = dff_coord['lng'],
                                      size = abs(dff_coord['lng']),
                                      hover_name= dff_coord['Unidade de Despesa'],
                                      )
    
        map_graph.update_layout(MAIN_CONFIG_2,
                                height = 900,
                                autosize = True,
                                title = 'Unidades da USP',
                                mapbox = {'accesstoken': mapbox_token, 'style':'light'},
                                showlegend=False,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                hoverlabel=HOVER_LINE_GRAPH,
                                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                mapbox_bounds={"west": -49.5, "east": -45, "south": -24, "north": -20.8})
        
        lista_graphs = []
        
        graph= dcc.Graph(figure = map_graph ,
                         config={"displayModeBar": False, "showTips": False, "scrollZoom": True},
                         id='map_graph'
                        )
        
        lista_graphs.append(graph)
        
        graph_ativos = dbc.Col([
            *lista_graphs
            ])
        
        # Indicadores
        lista_colunas = []
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Empenhado/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Empenhado (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Dotação Atual', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Dotação Atual (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago/Empenhado', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.1f}'.format(100*np.sum(df_filtered['Pago (R$)']) / np.sum(df_filtered['Empenhado (R$)'])), "%"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Dotação Atual em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Dotação Atual (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Empenhado em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Empenhado (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        col = dbc.Col([
         dbc.Card([
             dbc.CardBody([
                 dbc.Row([
                     dbc.Col([
                         html.Legend('Pago em Reais', className='textoQuartenario'),
                                                           
                                        ]),
                     ],),                                
                 dbc.Row([
                     dbc.Col([
                         html.H5(["",'{:,.2f}'.format((np.sum(df_filtered['Pago (R$)'])/ 1e6)).replace(',', '|').replace('.', ',').replace('|', '.'), " Mi"], className='textoPrincipal'),
                         ])
                     ])
                 ])
             ],className='cards_linha2'), 
         ], md=2, xs=6)
        lista_colunas.append(col)
        
        card_ativos= dbc.Row([
            *lista_colunas
            ])
        
        return [graph_ativos, card_ativos]    
                   
# =========  Run server  =========== #

if __name__ == "__main__":
    app.run_server(debug=True,port=8080,host='0.0.0.0')
 
 
 
 
 
             