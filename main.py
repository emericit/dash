"""
We were given a dataset about the players of the NBA 2013 season.
Given the names of the variables, and the data, we guessed what they mean with the
help of the site https://www.basketball-reference.com/about/glossary.html

We want to create a dashboard to compare the players and the teams.
The dashboard will have two pages:
- The first page will allow the user to choose the type of players he wants to compare 
(rookies or seniors)
- The second page will allow the user to choose the statistics for which he wants to
compare the teams
"""
import os
import dash
from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go

PLAYERS = '/players'
TEAMS = '/teams'

glossary = {"player"        : "Name of the player",
            "pos"           : "Position played",
            "age"           : "Age of the player, as of February 1st of the season",
            "bref_team_id"  : "3-letter team abbreviation",
            "g"             : "Games played",
            "gs"            : "Games started",
            "mp"            : "Minutes played",
            "fg."           : "Field goals percentage",
            "efg."          : "Effective field goals percentage",
            "ft."           : "Free throw percentage",
            "orb"           : "Offensive rebounds",
            "drb"           : "Defensive rebounds",
            "trb"           : "Total rebounds",
            "ast"           : "Assists",
            "stl"           : "Steals",
            "blk"           : "Blocks",
            "tov"           : "Turnovers",
            "pf"            : "Personal fouls",
            "pts"           : "Points",
            "season"        : "Season"}

positions = {'C': 'Center',
             'F': 'Forward',
             'G': 'Guard',
             'PF': 'Power Forward',
             'SF': 'Small Forward',
             'PG': 'Point Guard',
             'SG': 'Shooting Guard',
             'ALL': 'All positions'}

teams = """• Atlanta Hawks (ATL)
• Boston Celtics (BOS)
• Brooklyn Nets (BRK)
• Charlotte Hornets (CHA)
• Chicago Bulls (CHI)
• Cleveland Cavaliers (CLE)
• Detroit Pistons (DET)
• Indiana Pacers (IND)
• Miami Heat (MIA)
• Milwaukee Bucks (MIL)
• New York Knicks (NYK)
• Orlando Magic (ORL)
• Philadelphia 76ers (PHI)
• Toronto Raptors (TOR)
• Washington Wizards (WAS)
• Dallas Mavericks (DAL)
• Denver Nuggets (DEN)
• Golden State Warriors (GSW)
• Houston Rockets (HOU)
• Los Angeles Clippers (LAC)
• Los Angeles Lakers (LAL)
• Memphis Grizzlies (MEM)
• Minnesota Timberwolves (MIN)
• New Orleans Pelicans (NOP)
• Oklahoma City Thunder (OKC)
• Phoenix Suns (PHO)
• Portland Trail Blazers (POR)
• Sacramento Kings (SAC)
• San Antonio Spurs (SAS)
• Utah Jazz (UTA)"""
dict_teams = (dict(map(lambda x: (x[1], x[0].strip()), 
                       list(map(lambda x: x.replace(')', '').split('('), 
                                filter(lambda x: x!= '', map(lambda x: x.strip(), 
                                                             teams.split("•"))))))))
df_teams = pd.DataFrame.from_dict(dict_teams, orient='index', columns=['Team name']).reset_index(names='3-letter team abbreviation')
df_variables = pd.DataFrame.from_dict(glossary, orient='index', columns=['Variable description']).reset_index(names='Variable name')
df = pd.read_csv('nba_2013.csv').query("bref_team_id != 'TOT' and pos != 'G'")
numerical_variables = list(df.select_dtypes(exclude=['object']).columns)
df_head = df.head()
df_desc = df.describe(include="all").reset_index(names='statistics')
# in the first stage, we explored a bit the data. This part should not remain in the final version
if os.environ.get('DEBUG') is not None:
    print(df.head())
    print(df.info())
    tmp = df.select_dtypes(include=['object']).nunique()
    tmp = tmp[tmp > 1]
    tmp = tmp[tmp < df.shape[1]]
    categorical_variables = list(set(tmp.index) - {"bref_team_id"})
    print("Numerical variables  : ", ",".join(numerical_variables))
    print("Categorical variables: ", ",".join(categorical_variables))
positions_played = ['ALL'] + df['pos'].unique().tolist()


assert set(df.bref_team_id.unique()) <= set(dict_teams.keys()),\
    "Some teams in the dataset are not in the glossary"

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([html.Img(src="https://cdn.nba.com/logos/leagues/logo-nba.svg", alt="NBA", id="nba"),
              html.Button(dcc.Link('Home', href='/'), id="home_button"),
              html.Button(dcc.Link('Player Comparison', href=PLAYERS), id="player_button"),
              html.Button(dcc.Link('Team Comparison', href=TEAMS), id="team_button")], 
              id='navigation_bar'),
    html.Div(id='page_content')
])

index_page = html.Div([
    html.H1('NBA 2013 dataset'),
    html.P(['This is a dashboard to compare the players and the ', 
            html.A('teams', href='#teams_glossary'), ' of the NBA 2013 season.']),
    html.H2('Dataset source'),
    html.P(["""We were given a dataset about the players of the NBA 2013 season.
            Given the names of the variables, and the data, we guessed what they """,
            html.A('mean', href='#variables'),
            """ with the help of the site """, 
        html.A('basketball-reference', 
               href='https://www.basketball-reference.com/about/glossary.html')]),
    html.P(["""With this data, you can compare the players and the teams.
            The dashboard has two pages: """,
            html.Ul([html.Li([html.A('Player comparison', href=PLAYERS),
                              """: this page will allow you to choose the type of players you want 
                              to compare (rookies or seniors)"""]),
                     html.Li([html.A('Team comparison', href=TEAMS),
                              """: this page will allow you to choose the statistics for which you 
                              want to compare the teams"""])])]),
    html.H2('Dataset description'),
    html.H3('Dataframe head'),
    dash_table.DataTable(data=df_head.to_dict('records'),
                         columns=[{"name": i, "id": i} for i in df_head.columns], 
                         fixed_columns={'headers': True, 'data': 1},
                         fixed_rows={'headers': True, 'data': 0},
                         id='tbl_head', tooltip_header=glossary),
    html.H3('Dataframe summary'),
    dash_table.DataTable(data=df_desc.round(2).to_dict('records'),
                         columns=[{"name": i, "id": i} for i in df_desc.columns], 
                         id='tbl_desc',
                         fixed_columns={'headers': True, 'data': 1},
                         fixed_rows={'headers': True, 'data': 0},
                         tooltip_header=glossary),
    html.H2('References'),
    html.A(html.H3('Teams glossary'), id='teams_glossary'),
    dash_table.DataTable(data=df_teams.to_dict('records'),
                         columns=[{"name": i, "id": i} for i in df_teams.columns], 
                         fixed_columns={'headers': True, 'data': 1},
                         fixed_rows={'headers': True, 'data': 0},
                         id='tbl_teams'),
    html.A(html.H3('Variables'), id="variables"),
    dash_table.DataTable(data=df_variables.to_dict('records'),
                         columns=[{"name": i, "id": i} for i in df_variables.columns], 
                         fixed_columns={'headers': True, 'data': 1},
                         fixed_rows={'headers': True, 'data': 0},
                         id='tbl_variables'),
    ]
)

layout_players = html.Div([
    html.H1('Player Comparison'),
    html.H2('Choose the type of players you want to compare'),
    html.Div(dcc.Dropdown(id = 'player_dropdown',
                          options= [{'label': 'Rookies (under 24 yo)', 'value': 'rookies'},
                                    {'label': 'Seniors (24 yo or older)', 'value': 'seniors'}])),
    html.Div(id='players_table'),
])

@app.callback(Output(component_id='players_table', component_property='children'),
            [Input(component_id='player_dropdown', component_property='value')])
def update_players(value):
    if value == 'rookies':
        df_players = df[df['age'] < 24]
    elif value == 'seniors':
        df_players = df[df['age'] >= 24]
    else:
        return None
    return dash_table.DataTable(data=df_players.to_dict('records'),
                         columns=[{"name": i, "id": i} for i in df_players.columns], 
                         fixed_columns={'headers': True, 'data': 1},
                         fixed_rows={'headers': True, 'data': 0},
                         id='tbl_players', tooltip_header=glossary)

layout_teams = html.Div([
    html.H1('Team Comparison'),
    html.H2('Choose the statistic to compute'),
    html.Div(dcc.Dropdown(id='statistics_dropdown',
                          options=[{'label': v, 'value': k} for k, v in glossary.items() 
                                   if k in numerical_variables],
                          multi=True)),
    html.H2('If needed, split the analysis by position played'),
    html.Div(dcc.Slider(id='slider_teams',
                      min=0,
                      max=len(positions_played) - 1,
                      marks={index: str(positions[_]) for index, _ in enumerate(positions_played)},
                      value=0,
                      step=None)),
    html.Br(),
    html.Div(dcc.Graph(id='teams_graph', figure=go.Figure()), id="graph_container", style={"display": "none"}),
])

@app.callback([Output(component_id='teams_graph', component_property='figure'),
               Output(component_id='graph_container', component_property='style')],
              [Input(component_id='statistics_dropdown', component_property='value'),
               Input(component_id='slider_teams', component_property='value')])
def update_teams(statistics, position):
    if position is None:
        position = 0  # par défaut, on ne filtre pas par position
    if position not in range(len(positions_played)):
        return go.Figure(), {'display':'none'}
    if statistics is None or len(statistics) == 0:
        return go.Figure(), {'display':'none'}
    for statistic in statistics:
        if statistic not in numerical_variables:
            return go.Figure(), {'display':'none'}
    df1 = df.loc[:, statistics + ['bref_team_id', 'pos']]
    if position != 0:
        df1 = df1[df1['pos'] == positions_played[position]]
    df1 = df1.drop(columns=['pos']).groupby(by='bref_team_id').mean()
    n_graphs = len(statistics)
    n_cols = min(n_graphs, 3)
    n_rows = (n_graphs - 1) // 3 + 1
    fig = make_subplots(cols=n_cols, rows=n_rows)
    for index, statistic in enumerate(statistics):
        df_top5 = df1.sort_values(by=statistic, ascending=False).head(5).sort_values(by=statistic)
        title = glossary[statistic]
        if position != 0:
            title += ' (position = ' + positions[positions_played[position]] + ')'
        trace = go.Bar(y=df_top5.index, x=df_top5[statistic], name=title, orientation='h')
        fig.add_trace(col=(index%3)+1, row=(index//3)+1, trace=trace)
    fig['layout'].update(height=n_rows * 450)
    return fig, {'display':'block'}

@app.callback(dash.dependencies.Output('page_content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == PLAYERS:
        return layout_players
    elif pathname == TEAMS:
        return layout_teams
    elif pathname == "/":
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")