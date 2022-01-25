import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import plotly.express as px
import pandas as pd
import json
import datetime
import plotly.graph_objects as go
import plotly.graph_objects as go
import json
import os
import pandas as pd
import datetime
import plotly.graph_objs as go

import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server


mapbox_access_token = 'pk.eyJ1IjoiaGFtZWRtaW5hZWkiLCJhIjoiY2s3d3Bhemk0MDR3bDNrbG5wOHJqNmpjcSJ9.sTFiN0dxyLO7GgXJpqsoOQ'
if not mapbox_access_token:
    raise RuntimeError("Mapbox key not specified! Edit this file and add it.")


def get_latest_folder_path(folder):
    today = datetime.date.today()
    date_name = today.strftime('%Y-%m-%d')

    days_to_subtract = 1
    while not os.path.isdir(os.path.join(folder, date_name)):
        today = today - datetime.timedelta(days=days_to_subtract)
        date_name = today.strftime('%Y-%m-%d')

    return os.path.join(folder, date_name)


def read_agg_df_file():
    folder =r"C:\Users\HMinaeizae\PycharmProjects\COVID19_APP"
    df_maori_pacific = pd.read_csv(os.path.join(folder,'sa2_maori_pacific.csv'))
    df_maori_pacific = df_maori_pacific[df_maori_pacific['DHB of residence']=='Northland']

    df_all = pd.read_csv(os.path.join(folder,'sa2.csv'))
    df_all = df_all[df_all['DHB of residence']=='Northland']
    df_all['Ethnicity'] = 'all'
    df_all = pd.concat([df_all, df_maori_pacific])

    #df_all = df_all.set_index('SA2 2018')
    return df_all


# def latest_ministry_filename():
#     folder =r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP'
#     today = datetime.date.today()
#     date_name = today.strftime('%Y-%m-%d')
#     filename = 'Ministry_covid.csv'
#
#     days_to_subtract = 1
#     while not os.path.isfile(os.path.join(folder, filename)):
#         today = today - datetime.timedelta(days=days_to_subtract)
#         date_name = today.strftime('%Y-%m-%d')
#         filename = 'Ministry_covid_' + date_name + '.csv'
#     return filename

def read_ministry_file():
    file_name = 'Ministry_covid.csv'
    folder = r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP'
    return pd.read_csv(os.path.join(folder, file_name))

def create_dataframe_for_horizon_graph():
    df = read_ministry_file()
    df['At least partially vaccinated %'] = df['At least partially vaccinated %'].str.rstrip('%').astype('int')
    df['Fully vaccinated %'] = df['Fully vaccinated %'].str.rstrip('%').astype('int')
    data = {'Vaccination status':['Booster vaccinataion %', 'Fully vaccinated %','At least partially vaccinated %',  'Not Vaccinated']}
    Maori = pd.DataFrame(data)
    Maori['Ethnicity'] = 'Maori'
    Maori['Value'] = 0.0
    df_Maori = df[df['Ethnicity']=='Maori']

    Maori.iloc[0,2] = round(df_Maori.iloc[0,10]/10)
    Maori.iloc[1,2] =df_Maori.iloc[0,5]-Maori.iloc[0,2]
    Maori.iloc[2,2] = df_Maori.iloc[0,2]-Maori.iloc[1,2]-Maori.iloc[0,2]
    Maori.iloc[3,2] = 100.0 - Maori.iloc[2,2]-Maori.iloc[1,2]-Maori.iloc[0,2]

    # Pacific
    Pacific = pd.DataFrame(data)
    Pacific['Ethnicity'] = 'Pacific Peoples'
    Pacific['Value'] = 0
    df_Pacific = df[df['Ethnicity']=='Pacific Peoples']
    Pacific.iloc[0,2] = round(df_Pacific.iloc[0,10]/10)
    Pacific.iloc[1,2] =df_Pacific.iloc[0,5]-Pacific.iloc[0,2]
    Pacific.iloc[2,2] = df_Pacific.iloc[0,2]-Pacific.iloc[1,2]-Pacific.iloc[0,2]
    Pacific.iloc[3,2] = 100-Pacific.iloc[2,2]-Pacific.iloc[1,2]-Pacific.iloc[0,2]

    # all
    all = pd.DataFrame(data)
    all['Ethnicity'] = 'All Ethnicities'
    all['Value'] = 0
    df_all = df[df['Ethnicity'] == 'All']
    all.iloc[0, 2] = round(df_all.iloc[0, 10] / 10)
    all.iloc[1, 2] = df_all.iloc[0, 5] - all.iloc[0, 2]
    all.iloc[2, 2] = df_all.iloc[0, 2] - all.iloc[1, 2]-all.iloc[0, 2]
    all.iloc[3, 2] = 100 - all.iloc[2, 2]-all.iloc[1, 2]-all.iloc[0, 2]

    df_bar_graph = pd.concat([Maori, Pacific, all])
    x_data =[Maori['Value'].values.tolist(), Pacific['Value'].values.tolist(), all['Value'].values.tolist()]

    return df_bar_graph, x_data


def create_text_for_fully_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity'].str.contains(Ethnicity, case=False)]
    if ((Ethnicity=='all') | (Ethnicity=='All')):
        Text = str(df_filtered.iloc[0, 5])+ ' northlanders are fully vaccinated which is '+str(df_filtered.iloc[0, 4])+\
               ' people. '+str(df_filtered.iloc[0, 6]) +' more vaccination to reach 90%'
    else:
        Text = str(df_filtered.iloc[0, 5])+ ' '+Ethnicity+' are fully vaccinated which is '+str(df_filtered.iloc[0, 4])+\
               ' people. '+str(df_filtered.iloc[0, 6]) +' more vaccination to reach 90%'
    return Text

def create_text_for_partially_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity'].str.contains(Ethnicity, case=False)]
    if ((Ethnicity=='all') | (Ethnicity=='All')):
        Text = str(df_filtered.iloc[0, 2])+ ' northlanders are partially vaccinated which is '+str(df_filtered.iloc[0, 1])+\
               ' people. '+str(df_filtered.iloc[0, 3]) +' more vaccination to reach 90%'
    else:
        Text = str(df_filtered.iloc[0, 2])+ ' '+Ethnicity+' are partially vaccinated which is '+str(df_filtered.iloc[0, 1])+\
               ' people. '+str(df_filtered.iloc[0, 3]) +' more vaccination to reach 90%'
    return Text

def create_text_for_booster_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity'].str.contains(Ethnicity, case=False)]
    if ((Ethnicity=='all') | (Ethnicity=='All')):
        Text = str(round(df_filtered.iloc[0, 10]/10))+ '% northlanders have received booster vaccine which is '+str(f"{df_filtered.iloc[0, 9]:,}")+\
               ' people. '
    else:
        Text = str(round(df_filtered.iloc[0, 10]/10))+ '% '+Ethnicity+' have received booster vaccine which is '+str(f"{df_filtered.iloc[0, 9]:,}")+\
               ' people. '
    return Text

def create_text_for_not_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity'].str.contains(Ethnicity, case=False)]

    df_filtered['At least partially vaccinated']= df_filtered['At least partially vaccinated'].str.replace(',','').astype(float)
    df_filtered['Fully vaccinated'] = df_filtered['Fully vaccinated'].str.replace(',', '').astype(float)
    df_filtered['Population'] = df_filtered['Population'].str.replace(',', '').astype(float)


    if ((Ethnicity=='all') | (Ethnicity=='All')):


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% northlanders'+' are not vaccinated which is '+\
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1]))+\
               ' people. '
    else:


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% '+Ethnicity+' are not vaccinated which is '+ \
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])) +\
               ' people. '
    return Text


def create_figure_agegroup_number(ethnicity='Maori', vaccinestatus='At least partially vaccinated'):
    df_agegroup = pd.read_csv(r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\dhb_residence_uptake.csv')
    df_agegroup = df_agegroup[df_agegroup['DHB of residence']=='Northland']
    if ethnicity=='Maori' or ethnicity=='Pacific Peoples':
        df_agegroup =  df_agegroup[df_agegroup['Ethnic group']==ethnicity]
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'], color="Gender",
                          color_discrete_sequence=['rgba(38, 24, 74, 0.8)','rgba(122, 120, 168, 0.8)'])
        traceDHB.update_traces()
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return traceDHB
    else:
        #df_agegroup = df_agegroup[df_agegroup['Ethnic group'] == 'All']
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'], color="Gender",
                          color_discrete_sequence=['rgba(38, 24, 74, 0.8)','rgba(122, 120, 168, 0.8)'])
        traceDHB.update_traces()
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return traceDHB


def create_figure(ethnicity='Maori', vaccinestatus='At least partially vaccinated uptake per 1000 people'):
    df_agegroup = pd.read_csv(r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\dhb_residence_uptake.csv')
    df_agegroup = df_agegroup[df_agegroup['DHB of residence']=='Northland']
    if ethnicity=='Maori' or ethnicity=='Pacific Peoples':
        df_agegroup =  df_agegroup[df_agegroup['Ethnic group']==ethnicity]
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'],
                          color="Gender",  barmode="group", color_discrete_sequence=['rgba(38, 24, 74, 0.8)',
                                                                                     'rgba(122, 120, 168, 0.8)'])
        traceDHB.update_traces()
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return traceDHB
    else:
        #df_agegroup = df_agegroup[df_agegroup['Ethnic group'] == 'All']
        df = df_agegroup.groupby(['Age group','Gender']).mean().reset_index()

        traceDHB = px.bar(df, y=df[vaccinestatus], x=df['Age group'], color="Gender",  barmode="group",
                          color_discrete_sequence=['rgba(38, 24, 74, 0.8)','rgba(122, 120, 168, 0.8)'])
        traceDHB.update_traces()
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return traceDHB

traceDHB = create_figure(ethnicity='Maori', vaccinestatus='At least partially vaccinated uptake per 1000 people')
age_group_number = create_figure_agegroup_number(ethnicity='Maori', vaccinestatus='At least partially vaccinated')



full_path = os.path.join(r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\assets', 'SA2Final_GEOJason_new.json')
with open(full_path) as response:
    counties = json.load(response)

df = read_agg_df_file()

statuses = ['Fully vaccinated uptake', 'Partially vaccinated uptake', 'Booster vaccinated uptake']
for status in statuses:
    df[status] = df[status].replace('>950', 960)
    df[status] = df[status].astype(float)
    df[status] = df[status]/10


df= df[df['Ethnicity']=='Maori']
fig = px.choropleth_mapbox(df, geojson=counties, color=df['Fully vaccinated uptake'], color_continuous_scale='Purp',
                           featureidkey="properties.SA22018__1",
                           locations="SA2 2018",
                           mapbox_style="carto-positron",

                           zoom=7, center={"lat": -35.4594, "lon": 173.8898},
                           opacity=0.8

                           # range_color=[500, 1000],
                           # projection="mercator",

                           )
fig.update_geos(fitbounds='geojson', visible=True)

fig.update_layout(
    autosize=True,
    width=1000,
    height=600,
        )

df_bar_graph, x_data = create_dataframe_for_horizon_graph()
# second version

today = datetime.date.today()
date_name = today.strftime('%Y-%m-%d')
# top_labels = ['Booster<br>Vaccination', 'Fully<br>vaccinated %','At<br>least<br>partially<br>vaccinated', 'Not<br>Vaccinated'
#               ]
# colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
#           'rgba(122, 120, 168, 0.8)',
#           'rgba(190, 192, 213, 1)']
#
#
# y_data = ['Maori',
#           'Pacific Peoples', 'All Ethnicities' ]
#
# fig_maori = go.Figure()
# for i in range(0, len(x_data[0])):
#     for xd, yd in zip(x_data, y_data):
#         fig_maori.add_trace(go.Bar(
#             x=[xd[i]], y=[yd],
#             orientation='h',
#             marker=dict(
#                 color=colors[i],
#                 line=dict(color='rgb(248, 248, 249)', width=1)
#             )
#         ))
#
# fig_maori.update_layout(
#     xaxis=dict(
#         showgrid=False,
#         showline=False,
#         showticklabels=False,
#         zeroline=False,
#         domain=[0.15, 1]
#     ),
#     yaxis=dict(
#         showgrid=False,
#         showline=False,
#         showticklabels=False,
#         zeroline=False,
#     ),
#     barmode='stack',
#     paper_bgcolor='rgb(248, 248, 255)',
#     plot_bgcolor='rgb(248, 248, 255)',
#     margin=dict(l=120, r=10, t=140, b=80),
#     showlegend=False,
# )
#
# annotations = []
#
# for yd, xd in zip(y_data, x_data):
#     # labeling the y-axis
#     annotations.append(dict(xref='paper', yref='y',
#                             x=0.14, y=yd,
#                             xanchor='right',
#                             text=str(yd),
#                             font=dict(family='Arial', size=14,
#                                       color='rgb(67, 67, 67)'),
#                             showarrow=False, align='right'))
#     # labeling the first percentage of each bar (x_axis)
#     annotations.append(dict(xref='x', yref='y',
#                             x=xd[0] / 2, y=yd,
#                             text=str(xd[0]) + '%',
#                             font=dict(family='Arial', size=14,
#                                       color='rgb(248, 248, 255)'),
#                             showarrow=False))
#     # labeling the first Likert scale (on the top)
#     if yd == y_data[-1]:
#         annotations.append(dict(xref='x', yref='paper',
#                                 x=xd[0] / 2, y=1.1,
#                                 text=top_labels[0],
#                                 font=dict(family='Arial', size=14,
#                                           color='rgb(67, 67, 67)'),
#                                 showarrow=False))
#     space = xd[0]
#     for i in range(1, len(xd)):
#             # labeling the rest of percentages for each bar (x_axis)
#             annotations.append(dict(xref='x', yref='y',
#                                     x=space + (xd[i]/2), y=yd,
#                                     text=str(xd[i]) + '%',
#                                     font=dict(family='Arial', size=14,
#                                               color='rgb(248, 248, 255)'),
#                                     showarrow=False))
#             # labeling the Likert scale
#             if yd == y_data[-1]:
#                 annotations.append(dict(xref='x', yref='paper',
#                                         x=space + (xd[i]/2), y=3.1,
#                                         text=top_labels[i],
#                                         font=dict(family='Arial', size=12,
#                                                   color='rgb(67, 67, 67)'),
#                                         showarrow=False))
#             space += xd[i]
#
# fig_maori.update_layout(annotations=annotations)


fig_maori = px.bar(df_bar_graph, x="Value", y="Ethnicity", color='Vaccination status', orientation='h',
             title='Vaccination Status by ethnicity (%)',  color_discrete_sequence=['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
           'rgba(122, 120, 168, 0.8)',
           'rgba(190, 192, 213, 1)'])

#color_discrete_sequence = px.colors.qualitative.Prism
colors = {
    'background': '#000000',
    'text': '#bdbdbd',
    'Section': '#525252',
    'textColor1': '#e32e2e',
    'textColor2': '#fab91c',
    'textColor3': '#0545d8',
    'textColor4': '#ffffff',
    'White': '#ffffff'
}

lego_image_filename = r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\Photos\logo-landscape-reduc.png' # replace with your own image
lego_encoded_image = base64.b64encode(open(lego_image_filename, 'rb').read()).decode('ascii')

covid_image_filename = r'C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\assets\2492-NDHB-Nga-Tai-Ora-Only.png' # replace with your own image
covid_encoded_image = base64.b64encode(open(covid_image_filename, 'rb').read()).decode('ascii')

app.layout = html.Div([
    html.Div([
            html.Div([
            html.Img(src='data:image/png;base64,{}'.format(lego_encoded_image),
                        style={
                                 "width": "400px",
                                 "height": "auto",
                                "margin-bottom": "5px",
                            }
                     )
                ],
                   className="pretty_container one-half column",
                   style={ 'backgroundColor': '#0C48F4' }
                   #className="pretty_container one-half column",
            )
            ,
            html.Div([

                html.Img(src='data:image/png;base64,{}'.format(covid_encoded_image),
                         style={
                             "width": "400px",
                             "height": "auto",
                             "margin-bottom": "5px",
                         }
                         )
            ],
                    className="pretty_container one-half column",
                 style={ 'backgroundColor': '#FFFFFF'}
                #className="pretty_container one-half column",
            )
        ],
        className=" pretty_container row flex-display"
    )
    ,
    html.Div([dcc.Graph(figure=fig_maori, id="Maori-Graph", responsive=True,
                            # style={
                            #     "width": "100%",
                            #     "height": "100%",
                            #     "display": "block",
                            #     "margin-left": "auto",
                            #     "margin-right": "auto",
                            # }
                        )],
             # style = {'margin':'auto'},
             className="pretty_container")

             #
             # id="maori stoc",
             #
             # )


    ,
    html.Div([
        html.Div([

            html.H4(children=create_text_for_fully_vaccination(Ethnicity='Maori') , id='text_fully_vac')
        ],
            className="pretty_container one-third column",
            id="H4",
        ),
        html.Div([

            html.H4(children=create_text_for_partially_vaccination(Ethnicity='Maori'), id='text_partially_vac')
        ],
            className="pretty_container one-third column",
            id="H3",
        ),
        html.Div([

            html.H3(children=create_text_for_booster_vaccination(Ethnicity='Maori'), id='text-no-vaccination')
        ],
            className="pretty_container one-third column",
            id="H2",
        ),



    ],
    className = "pretty_container row container-display",
    id = "Text"
),
   # html.Div([

        # Design Tab for Graph

    html.Div([
        html.Div([

            html.Div(
                [html.Label('vaccination status'),
                 dcc.RadioItems(
                     id="dropdown",
                     options=[
                         {'label': u'Partially vaccinated (First does)', 'value': 'Partially vaccinated uptake'},
                         {'label': u'Fully vaccinated (second does)', 'value': 'Fully vaccinated uptake'},
                         {'label': u'Boosters',                      'value': 'Booster vaccinated uptake'},

                     ],
                     value='Fully vaccinated uptake'
                 ), ],
                id="dropdown Div",
                className="pretty_container one-half column",
            ),

            html.Div(
                [html.Label('Ethnicity'),
                 dcc.RadioItems(
                     id="Ethdropdown",
                     options=[
                         {'label': 'Maori', 'value': 'Maori'},
                         {'label': u'Pacific Islanders', 'value': 'Pacific Peoples'},
                         {'label': u'All Ethnicity', 'value': 'all'}
                     ],
                     value='Maori'
                 ), ],
                id="Ethnicity dropdown Div",
                className="pretty_container one-half column",
            ),

        ],
            className="row container-display",
        ),
        html.Div([
                html.Div(
                    [dcc.Graph(figure=fig, id="choropleth")],
                    # style={"width": 'auto', 'height': 'auto'},
                    # [dcc.Graph(id="choropleth")],
                    # id="countGraphContainer",
                    className="pretty_container",
                ),
            html.Div([
                html.H1('Vaccination by Age Group'),
                dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
                    dcc.Tab(label='Dose uptake per 1000 people', value='tab-1-example-graph'),
                    dcc.Tab(label='Number by age group', value='tab-2-example-graph'),
                ]),
                html.Div(id='tabs-content-example-graph')

            ],
                className="pretty_container"
            )

        ],
        className="pretty_container"
        )
        ],

        id='graph',
        className="pretty_container",
    ),



    #],

   #  # dcc.Store stores the intermediate value
   # # dcc.Store(id='intermediate-value'),
   #  className = "row container-display",
   #  ),


   html.Div(
       #[ html.P(children='the data in this app is based on the ', id='fixed text')]
       [dcc.Markdown('''The first and second doses of COVID vaccination data are based on the [Ministry of health data](https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-data-and-statistics/covid-19-vaccine-data) data and updated weekly. The booster vaccination is based on Northland Public Health Unit intelligence group data and updated daily. The last update is on {} '''.format(date_name))]
       , id= 'graph vaccine Over Time',
       className="pretty_container columns"




   )


])

# call Back
# @app.callback(Output('intermediate-value', 'data'), Input('dropdown', 'value'))
# def clean_data(value):
#      # some expensive data processing step
#      geo_df = update_value_geofile(ethcicity='Maori', status='value')
#
#      # more generally, this line would be
#      # json.dumps(cleaned_df)
#      return cleaned_df.to_json(date_format='iso', orient='split')
@app.callback(
    dash.dependencies.Output('text-no-vaccination', 'children'),
    [ dash.dependencies.Input('Ethdropdown', 'value')]
     )

def update_novacc(Ethdropdown):
    Text = create_text_for_booster_vaccination(Ethdropdown)
    return Text



@app.callback(
    dash.dependencies.Output('text_fully_vac', 'children'),
    [ dash.dependencies.Input('Ethdropdown', 'value')]
     )

def update_fullyvacc(Ethdropdown):
    Text = create_text_for_fully_vaccination(Ethdropdown)
    return Text

@app.callback(
    dash.dependencies.Output('text_partially_vac', 'children'),
    [ dash.dependencies.Input('Ethdropdown', 'value')]
     )

def update_fullyvacc(Ethdropdown):
    Text = create_text_for_partially_vaccination(Ethdropdown)
    return Text



@app.callback(
    dash.dependencies.Output("choropleth", 'figure'),
    [dash.dependencies.Input('dropdown', 'value'),
     dash.dependencies.Input('Ethdropdown', 'value')]
     )

def update_mapSocial(dropdown, Ethdropdown):

    df = read_agg_df_file()
    df = df[ df['Ethnicity']==Ethdropdown]

    status = dropdown
    df[status] = df[status].replace('>950', 960)
    df[status] = df[status].astype(float)
    df[status] = df[status] / 10

    fig = px.choropleth_mapbox(df, geojson=counties, color=df[dropdown], color_continuous_scale='Purp',
                               featureidkey="properties.SA22018__1",
                               locations="SA2 2018",
                               mapbox_style="carto-positron",

                               zoom=7, center={"lat": -35.4594, "lon": 173.8898},
                               opacity=0.8

                               # range_color=[500, 1000],
                               # projection="mercator",

                               )
    fig.update_geos(fitbounds='geojson', visible=True)
    fig.update_layout(
        autosize=True,
        width=1000,
        height=600,
    )
    return fig


# Tab Call Back
@app.callback(Output('tabs-content-example-graph', 'children'),
              [dash.dependencies.Input('dropdown', 'value'),
               dash.dependencies.Input('Ethdropdown', 'value'),
               dash.dependencies.Input('tabs-example-graph', 'value')]
              )
def render_content(dropdown, Ethdropdown,tab):



    if tab == 'tab-1-example-graph':
        if dropdown == 'Partially vaccinated uptake':
            dropdown = 'At least partially vaccinated uptake per 1000 people'
        else:
            dropdown = 'Fully vaccinated uptake per 1000 people'
        traceDHB = create_figure(ethnicity=Ethdropdown, vaccinestatus=dropdown)
        return html.Div([
            html.H3('Dose uptake per 1000 people'),
            dcc.Graph(
                id='graph-1-tabs',
                figure=traceDHB

            )
        ])
    elif tab == 'tab-2-example-graph':
        if dropdown == 'Partially vaccinated uptake':
            dropdown = 'At least partially vaccinated'
        else:
            dropdown = 'Fully vaccinated'
        traceDHB = create_figure_agegroup_number(ethnicity=Ethdropdown, vaccinestatus=dropdown)
        return html.Div([
            html.H3('Number of doses administered'),
            dcc.Graph(
                id='graph-2-tabs',
                figure=traceDHB

            )
        ])



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
