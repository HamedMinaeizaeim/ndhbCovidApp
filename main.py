import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import plotly.express as px
import pandas as pd
import json
import datetime
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
    folder =r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/"
    df_maori_pacific = pd.read_csv(folder+'sa2_maori_pacific.csv')
    df_maori_pacific = df_maori_pacific[df_maori_pacific['DHB']=='Northland']

    df_all = pd.read_csv(os.path.join(folder,'sa2.csv'))
    df_all = df_all[df_all['DHB']=='Northland']
    df_all['ETHNICITY'] = 'all'
    df_all = pd.concat([df_all, df_maori_pacific])

    #df_all = df_all.set_index('SA2 2018')
    return df_all


def latest_ministry_filename():
    folder =r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/"
    today = datetime.date.today()
    date_name = today.strftime('%Y-%m-%d')
    filename = 'Ministry_covid_'+date_name+'.csv'

    days_to_subtract = 1
    while not os.path.isfile(os.path.join(folder, filename)):
        today = today - datetime.timedelta(days=days_to_subtract)
        date_name = today.strftime('%Y-%m-%d')
        filename = 'Ministry_covid_' + date_name + '.csv'
    return filename

def read_ministry_file():
    file_name = 'Ministry_covid_2021-12-08.csv'
    folder = r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/"
    return pd.read_csv(folder+ file_name)

def create_text_for_fully_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity']==Ethnicity]
    if Ethnicity=='all':
        Text = str(df_filtered.iloc[0, 5])+ ' northlanders are fully vaccinated which is '+str(df_filtered.iloc[0, 4])+\
               ' people. '+str(df_filtered.iloc[0, 6]) +' more vaccination to reach 90%'
    else:
        Text = str(df_filtered.iloc[0, 5])+ ' '+Ethnicity+' are fully vaccinated which is '+str(df_filtered.iloc[0, 4])+\
               ' people. '+str(df_filtered.iloc[0, 6]) +' more vaccination to reach 90%'
    return Text

def create_text_for_partially_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity']==Ethnicity]
    if Ethnicity=='all':
        Text = str(df_filtered.iloc[0, 2])+ ' northlanders are partially vaccinated which is '+str(df_filtered.iloc[0, 1])+\
               ' people. '+str(df_filtered.iloc[0, 3]) +' more vaccination to reach 90%'
    else:
        Text = str(df_filtered.iloc[0, 2])+ ' '+Ethnicity+' are partially vaccinated which is '+str(df_filtered.iloc[0, 1])+\
               ' people. '+str(df_filtered.iloc[0, 3]) +' more vaccination to reach 90%'
    return Text

def create_text_for_not_vaccination(Ethnicity='Maori'):
    df = read_ministry_file()
    df_filtered = df[df['Ethnicity']==Ethnicity]
    df_filtered['At least partially vaccinated']= df_filtered['At least partially vaccinated'].str.replace(',','').astype(float)
    df_filtered['Fully vaccinated'] = df_filtered['Fully vaccinated'].str.replace(',', '').astype(float)
    df_filtered['Population'] = df_filtered['Population'].str.replace(',', '').astype(float)



    if Ethnicity=='all' or Ethnicity=='All':


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% northlanders'+' are not vaccinated which is '+\
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1]))+\
               ' people. '
    else:


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% '+Ethnicity+' are not vaccinated which is '+ \
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])) +\
               ' people. '
    return Text


def create_figure_agegroup_number(ethnicity='Maori', vaccinestatus='First dose administered'):
    df_agegroup = pd.read_csv(r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/assets/dhb_residence_uptake.csv")
    df_agegroup = df_agegroup[df_agegroup['DHB of residence']=='Northland']
    if ethnicity=='Maori' or ethnicity=='Pacific Peoples':
        df_agegroup =  df_agegroup[df_agegroup['Ethnic group']==ethnicity]
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'], color="Gender")
        traceDHB.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return traceDHB
    else:
        #df_agegroup = df_agegroup[df_agegroup['Ethnic group'] == 'All']
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'], color="Gender")
        traceDHB.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return traceDHB


def create_figure(ethnicity='Maori', vaccinestatus='First dose uptake per 1000 people'):
    df_agegroup = pd.read_csv(r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/assets/dhb_residence_uptake.csv")
    df_agegroup = df_agegroup[df_agegroup['DHB of residence']=='Northland']
    if ethnicity=='Maori' or ethnicity=='Pacific Peoples':
        df_agegroup =  df_agegroup[df_agegroup['Ethnic group']==ethnicity]
        traceDHB = px.bar(df_agegroup, y=df_agegroup[vaccinestatus], x=df_agegroup['Age group'],  color="Gender",  barmode="group" )
        traceDHB.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return traceDHB
    else:
        #df_agegroup = df_agegroup[df_agegroup['Ethnic group'] == 'All']
        df = df_agegroup.groupby(['Age group','Gender']).mean().reset_index()

        traceDHB = px.bar(df, y=df[vaccinestatus], x=df['Age group'], color="Gender",  barmode="group")
        traceDHB.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        traceDHB.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return traceDHB

traceDHB = create_figure(ethnicity='Maori', vaccinestatus='First dose uptake per 1000 people')
age_group_number = create_figure_agegroup_number(ethnicity='Maori', vaccinestatus='First dose administered')

full_path = (r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/assets/"+ 'SA2Final_GEOJason_new.json')
with open(full_path) as response:
    counties = json.load(response)

df = read_agg_df_file()
df= df[df['ETHNICITY']=='Maori']
status = ' FIRST DOSE UPTAKE '
df[status] = df[status].replace(' >950 ', 960)
df[status] = df[status].astype(float)
df[status] = df[status]/10

fig = px.choropleth_mapbox(df, geojson=counties, color=df[' FIRST DOSE UPTAKE '], color_continuous_scale='viridis',
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

lego_image_filename = r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/assets/logo-landscape-reduc.png" # replace with your own image
lego_encoded_image = base64.b64encode(open(lego_image_filename, 'rb').read()).decode('ascii')

covid_image_filename =r"https://github.com/HamedMinaeizaeim/ndhbCovidApp/tree/master/assets/assets/3146-NDHB-COVID19-Ka-Pai-Website-Banner-1170x215px-4.png" # replace with your own image
covid_encoded_image = base64.b64encode(open(covid_image_filename, 'rb').read()).decode('ascii')

app.layout = html.Div([
    html.Div([
            html.Div([
            html.Img(src='data:image/png;base64,{}'.format(lego_encoded_image),
                        style={
                                "height": "100px",
                                 "width": "auto",
                                "margin-bottom": "5px",
                            }
                     )
                ],
                   style={'width': '48%','display': 'inline-block', 'textAlign': 'center', 'padding': 10, 'backgroundColor': '#0C48F4'}
            )
            ,
            html.Div([

                html.Img(src='data:image/png;base64,{}'.format(covid_encoded_image),
                         style={
                             "height": "100px",
                             "width": "auto",
                             "margin-bottom": "5px",
                         }
                         )
            ],
                style={'width': '48%','display': 'inline-block', 'textAlign': 'center', 'padding': 10, 'backgroundColor': '#0C48F4'}
            )
        ],
       # className="row flex-display"
    )
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

            html.H3(children=create_text_for_not_vaccination(Ethnicity='Maori'), id='text-no-vaccination')
        ],
            className="pretty_container one-third column",
            id="H2",
        ),



    ],
    className = "row container-display",
    id = "Text"
),
    html.Div([

        # Design Tab for Graph
        html.Div([
            html.H1('Vaccination by Age Group'),
            dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
                dcc.Tab(label='% by age group', value='tab-1-example-graph'),
                dcc.Tab(label='Number by age group', value='tab-2-example-graph'),
            ]),
            html.Div(id='tabs-content-example-graph')


        ],
            className = "pretty_container one-third column"
        ),

        html.Div([
            html.Div([


                    html.Div(
                        [   html.Label('vaccination status'),
                            dcc.RadioItems(
                            id="dropdown",
                            options=[
                                {'label': u'Partially vaccinated', 'value': ' FIRST DOSE UPTAKE '},
                                {'label': u'Fully vaccinated', 'value': ' SECOND DOSE UPTAKE '}

                            ],
                            value=' SECOND DOSE UPTAKE '
                             ),],
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
            className = "row container-display",
            ),
            html.Div(
                [dcc.Graph(figure=fig,id="choropleth")],
                #style={"width": '90vh', 'height': '90vh'},
                #[dcc.Graph(id="choropleth")],
                # id="countGraphContainer",
                className="pretty_container",
            ),
        ],
            id='graph',
            className = "pretty_container two-thirds column",
        ),


    ],

    # dcc.Store stores the intermediate value
   # dcc.Store(id='intermediate-value'),
    className = "row container-display",
    ),
   html.Div(
       []
       , id= 'graph vaccine Over Time',
       className="pretty_container"




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
    Text = create_text_for_not_vaccination(Ethdropdown)
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
    df = df[ df['ETHNICITY']==Ethdropdown]
    status = dropdown
    df[status] = df[status].replace(' >950 ', 960)
    df[status] = df[status].astype(float)
    df[status] = df[status] / 10

    fig = px.choropleth_mapbox(df, geojson=counties, color=df[dropdown], color_continuous_scale='viridis',
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
        if dropdown == ' FIRST DOSE UPTAKE ':
            dropdown = 'First dose uptake per 1000 people'
        else:
            dropdown = 'Second dose uptake per 1000 people'
        traceDHB = create_figure(ethnicity=Ethdropdown, vaccinestatus=dropdown)
        return html.Div([
            html.H3('Dose uptake per 1000 people'),
            dcc.Graph(
                id='graph-1-tabs',
                figure=traceDHB

            )
        ])
    elif tab == 'tab-2-example-graph':
        if dropdown == ' FIRST DOSE UPTAKE ':
            dropdown = 'First dose administered'
        else:
            dropdown = 'Second dose administered'
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
