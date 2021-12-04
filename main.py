import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import geopandas as gpd
import json
# import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib
import matplotlib.cm as cm
import os
import pandas as pd
import datetime
import plotly.graph_objs as go
from scipy.interpolate import interp1d
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server


mapbox_access_token = 'pk.eyJ1IjoiaGFtZWRtaW5hZWkiLCJhIjoiY2s3d3Bhemk0MDR3bDNrbG5wOHJqNmpjcSJ9.sTFiN0dxyLO7GgXJpqsoOQ'
if not mapbox_access_token:
    raise RuntimeError("Mapbox key not specified! Edit this file and add it.")


def read_geo_file():
    return gpd.read_file(os.path.join(full_path_geojson, 'SA2Final_GEOJason.json'))

def initial_setup_geo_file():
    geo_file = read_geo_file()
    geo_file = geo_file.set_index('SA22018__1')
    geo_file['HOVER'] = np.nan
    # initial assessment
    geo_file['LON'] = geo_file['geometry'].centroid.x
    geo_file['LAT'] = geo_file['geometry'].centroid.y

    lon = geo_file['LON'][0]
    lat = geo_file['LAT'][0]

    return geo_file, lon, lat

def get_latest_folder_path(folder):
    today = datetime.date.today()
    date_name = today.strftime('%Y-%m-%d')

    days_to_subtract = 1
    while not os.path.isdir(os.path.join(folder, date_name)):
        today = today - datetime.timedelta(days=days_to_subtract)
        date_name = today.strftime('%Y-%m-%d')

    return os.path.join(folder, date_name)


def read_agg_df_file():
    folder =r"C:\Users\HMinaeizae\PycharmProjects\COVID19_APP\assets\nz-covid-data\vaccine-data"
    df_maori_pacific = pd.read_csv(os.path.join(get_latest_folder_path(folder),'sa2_maori_pacific.csv'))
    df_maori_pacific = df_maori_pacific[df_maori_pacific['DHB']=='Northland']

    df_all = pd.read_csv(os.path.join(get_latest_folder_path(folder),'sa2.csv'))
    df_all = df_all[df_all['DHB']=='Northland']
    df_all['ETHNICITY'] = 'all'
    df_all = pd.concat([df_all, df_maori_pacific])

    df_all = df_all.set_index('SA2 2018')
    return df_all

def update_value_geofile(ethcicity='Maori', status=' FIRST DOSE UPTAKE '):
    df = read_agg_df_file()

    geo_file, lon, lat = initial_setup_geo_file()
    df_updated = df[(df['ETHNICITY']==ethcicity)]
    df_updated[status] = df_updated[status].replace(' >950 ', 960)
    df_updated[status] = df_updated[status].astype(float)
    df_updated[status] = df_updated[status]/10

    geo_file['NUM_LEP'] = np.nan
    unique_sa2_names = geo_file.index.tolist()
    df_name_list = df_updated.index.tolist()
    all_join_names =[name for name in unique_sa2_names if name in df_name_list]
    for unique_sa2_name in all_join_names:
        geo_file.loc[unique_sa2_name,'NUM_LEP'] = df_updated.loc[unique_sa2_name, status]
    geo_file = geo_file.dropna(subset=['NUM_LEP'])
    return geo_file

# Read vaccination from Ministry website
def latest_ministry_filename():
    folder =r'C:\Users\HMinaeizae\PycharmProjects\Agg_Vaccination\Data'
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
    file_name = latest_ministry_filename()
    folder = r'C:\Users\HMinaeizae\PycharmProjects\Agg_Vaccination\Data'
    return pd.read_csv(os.path.join(folder, file_name))

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
    df_filtered['Partially vaccinated']= df_filtered['Partially vaccinated'].str.replace(',','').astype(float)
    df_filtered['Fully vaccinated'] = df_filtered['Fully vaccinated'].str.replace(',', '').astype(float)
    df_filtered['Population'] = df_filtered['Population'].str.replace(',', '').astype(float)


    if Ethnicity=='all':


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% northlanders'+' are not vaccinated which is '+\
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1]))+\
               ' people. '
    else:


        Text = str(round(((df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])/df_filtered.iloc[0, 7])*100))+ '% '+Ethnicity+' are not vaccinated which is '+ \
               str(int(df_filtered.iloc[0, 7]-df_filtered.iloc[0, 1])) +\
               ' people. '
    return Text








full_path_geojson = r'\assets'
geo_file = gpd.read_file(os.path.join(full_path_geojson, 'SA2Final_GEOJason.json'))
geo_file = geo_file.set_index('SA22018__1')
geo_file['HOVER'] = np.nan
# initial assessment
geo_file['LON'] = geo_file['geometry'].centroid.x
geo_file['LAT'] = geo_file['geometry'].centroid.y

lon = geo_file['LON'][0]
lat = geo_file['LAT'][0]

lengthdata = geo_file['LON'].count()

# Read data from CSV
df = read_agg_df_file()
#df = df.set_index('SA2 2018')




geo_file = update_value_geofile(ethcicity='Maori', status=' FIRST DOSE UPTAKE ')



map_layout = {
    'data': [{
        'lon': geo_file['LON'],
        'lat': geo_file['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.8,

            'colorbar': dict(
                thicknessmode="fraction",
                title="Time of<br>Day",
                x=0.935,
                xpad=0,
                nticks=24,
                tickfont=dict(
                    color='white'
                ),
                titlefont=dict(
                    color='white'
                ),
                titleside='left'
            ),
        },
        'type': 'scattermapbox',
        'name': 'Portland LEP',
        'text': geo_file['HOVER'],
        'hoverinfo': 'text',
        'anotation':  [dict(
		showarrow = True,
		align = 'right',
		text = '<b>Test1<br>Test2</b>',
		x = 0.95,
		y = 0.95,
	    )],
        'showlegend': False,
    }],
    'layout': {
        'autosize': True,
        'hovermode': 'closest',
        'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0},
        'mapbox': {
            'accesstoken': mapbox_access_token,
            'center': {
                'lat': lat,
                'lon': lon
            },
            'zoom': 7.0,
            'bearing': 0.0,
            'pitch': 0.0,
        },
    }
}

mcolors = matplotlib.colors
def set_overlay_colors(dataset):
    """Create overlay colors based on values

    :param dataset: gpd.Series, array of values to map colors to

    :returns: dict, hex color value for each language or index value
    """
    minima = dataset.min()
    maxima = dataset.max()
    norm = mcolors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.viridis)
    colors = [mcolors.to_hex(mapper.to_rgba(v)) for v in dataset]

    overlay_color = {
        idx: shade
        for idx, shade in zip(dataset.index, colors)
    }

    return overlay_color


def set_colors_Scale(dataset):
    """Create overlay colors based on values

    :param dataset: gpd.Series, array of values to map colors to

    :returns: dict, hex color value for each language or index value
    """

    dataset=dataset.sort_values (ascending=True)
    minima = dataset.min()
    maxima = dataset.max()
    databetween=np.linspace(minima, maxima,10)
    RelativeValue=np.linspace(0, 1 ,10)
    norm = mcolors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.viridis)

    w, h = 2, len(databetween)
    colorscale = [[0 for x in range(w)] for y in range(h)]

    for i in range(0, len(databetween)):
         colorsmaxArray = [mcolors.to_rgb(mapper.to_rgba(databetween[i]))]
         colorsmaxArray=colorsmaxArray[0]
         colorsmaxArray=tuple(map(lambda x: x*255, colorsmaxArray))
         colorsmax='rgb('+str(int(colorsmaxArray[0]))+','+str(int(colorsmaxArray[1]))+','+str(int(colorsmaxArray[2]))+')'
         colorscale[i][0] =  RelativeValue[i]
         colorscale[i][1] = colorsmax
    return colorscale


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

lego_image_filename = r'\Photos\logo-landscape-reduc.png' # replace with your own image
lego_encoded_image = base64.b64encode(open(lego_image_filename, 'rb').read()).decode('ascii')

covid_image_filename = r'\assets\3146-NDHB-COVID19-Ka-Pai-Website-Banner-1170x215px-4.png' # replace with your own image
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
            className="pretty_container one-fourth column",
            id="H4",
        ),
        html.Div([

            html.H4(children=create_text_for_partially_vaccination(Ethnicity='Maori'), id='text_partially_vac')
        ],
            className="pretty_container one-fourth column",
            id="H3",
        ),
        html.Div([

            html.H3(children=create_text_for_not_vaccination(Ethnicity='Maori'), id='text-no-vaccination')
        ],
            className="pretty_container one-fourth column",
            id="H2",
        ),
        html.Div([

            html.H3(children='Number of cases in hospital')
        ],
            className="pretty_container one-fourth column",
            id="H1",
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
                dcc.Tab(label='Tab One', value='tab-1-example-graph'),
                dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
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
                                {'label': 'Dose 1 only', 'value': ' FIRST DOSE UPTAKE '},
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
                                 {'label': u'All', 'value': 'all'}
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
                [dcc.Graph(id="choropleth")],
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
    #tmpSocial = map_layoutSocial.copy()
    #lep_dfFilterSocial = ValuesforSocialMap(SocialEconmic_df, SocialDropDown)
    print(dropdown)
    geo_file = update_value_geofile(ethcicity=Ethdropdown, status=dropdown)

    colors = set_overlay_colors(geo_file.NUM_LEP)
    colorscaleSocial = set_colors_Scale(geo_file.NUM_LEP)

    # Create a layer for each region colored by LEP value
    layers = [{
        'name': dropdown,
        'source': json.loads(geo_file.loc[geo_file.index == i, :].to_json()),
        'sourcetype': 'geojson',
        'type': 'fill',
        'opacity': 1.0,
        'color': colors[i]
    } for i in geo_file.index]

    data = [{
        'lon': geo_file['LON'],
        'lat': geo_file['LAT'],
        'mode': 'markers',
        'marker': {
            'opacity': 0.8,
            'reversescale': False,
            'autocolorscale': False,
            'colorscale': colorscaleSocial,
            'cmin': geo_file['NUM_LEP'].min(),
            'color': geo_file['NUM_LEP'],
            'cmax': geo_file['NUM_LEP'].max(),
            'colorbar': dict(
                thicknessmode="fraction",
                title=dict(text=dropdown,
                           side='right'),
                x=0.1,
                xanchor='right',
            xpad=0,
                nticks=24,
                tickfont=dict(
                    color='black'
                ),
                titlefont=dict(
                    color='black'
                ),
                titleside='black'
            ),
        },

        'type': 'scattermapbox',
        'text': geo_file['HOVER'],
        'hoverinfo': 'text',
        'showlegend': False,
    }]
    geo_file['NUM_LEP'].fillna(0, inplace=True)
    # tmpSocial['data'][0]['text'] = 'Area unit name: ' + lep_dfFilterSocial.AU_NAME + \
    # '<br /> '+SocialDropDown+'<br /> '+ lep_dfFilterSocial.NUM_LEP.astype(int).astype(str)+"%"

    map_layout['data'] = data
    # tmpSocial['data'][0]['text'] = 'Area unit name: ' + lep_dfFilterSocial.AU_NAME + \
    #                                '<br /> ' + SocialDropDown + '<br /> ' + lep_dfFilterSocial.NUM_LEP.astype(
    #     int).astype(str)
    map_layout['layout']['mapbox']['layers'] = layers

    return map_layout


# Tab Call Back
@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return html.Div([
            html.H3('Tab content 1'),
            dcc.Graph(
                id='graph-1-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [3, 1, 2],
                        'type': 'bar'
                    }]
                }
            )
        ])
    elif tab == 'tab-2-example-graph':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
