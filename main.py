"""
<p>We were given a dataset about the players of the NBA 2013 season.
Given the names of the variables, and the data, we guessed what they mean with the
help of the site <a href='https://www.basketball-reference.com/about/glossary.html'>
https://www.basketball-reference.com/about/glossary.html</a>
</p>

<p>We want to create a dashboard to compare the players and the teams.
The dashboard will have two pages:
<ul>
<li> The first page will allow the user to choose the type of players he wants to compare 
(rookies or seniors) </li>
<li> The second page will allow the user to choose the statistics for which he wants to
compare the teams </li>
</ul></p>
"""
import os
import bs4 as bs
import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px 
from dash.dependencies import Output,Input

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

df = pd.read_csv('nba_2013.csv').query("bref_team_id != 'TOT' and pos != 'G'")
numerical_variables = list(df.select_dtypes(exclude=['object']).columns)
tmp = df.select_dtypes(include=['object']).nunique()
tmp = tmp[tmp > 1]
tmp = tmp[tmp < df.shape[1]]
categorical_variables = list(set(tmp.index) - {"bref_team_id"})
# in the first stage, we explored a bit the data. This part should not remain in the final version
if os.environ.get('DEBUG') is not None:
    print(df.head())
    print(df.info())
    print("Numerical variables  : ", ",".join(numerical_variables))
    print("Categorical variables: ", ",".join(categorical_variables))
positions_played = ['ALL'] + df['pos'].unique().tolist()

def convert_html_to_dash(el, style=None):
    ALLOWED =  {'div','span','a','hr','br','p','b','i','u','s','h1','h2','h3','h4','h5','h6','ol','ul','li',
                'em','strong','cite','tt','pre','small','big','center','blockquote','address','font','img',
                'table','tr','td','caption','th','textarea','option','thead','tbody','tfoot','col','colgroup'}
    def __extract_style(el):
        if not el.attrs.get("style"):
            return None
        return {k.strip():v.strip() for k,v in [x.split(":") for x in el.attrs["style"].split(";") 
                                                if ":" in x]}
    if type(el) is str:
        return convert_html_to_dash(bs.BeautifulSoup(el,'html.parser'))
    if type(el) == bs.element.NavigableString:
        return str(el)
    else:
        name = el.name
        style = __extract_style(el) if style is None else style
        contents = [convert_html_to_dash(x) for x in el.contents]
        if name.title().lower() not in ALLOWED:        
            return contents[0] if len(contents)==1 else html.Div(contents)
        return getattr(html, name.title())(contents, style=style)

assert set(df.bref_team_id.unique()) <= set(dict_teams.keys()), "Some teams in the dataset are not in the glossary"

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, 
                #external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([html.Img(src="https://cdn.nba.com/logos/leagues/logo-nba.svg", alt="NBA logo", id="nba_logo"),
              html.Button(dcc.Link('Home', href='/'), id="home_button"),
              html.Button(dcc.Link('Player Comparison', href='/players'), id="player_button"),
              html.Button(dcc.Link('Team Comparison', href='/teams'), id="team_button")], id='navigation-bar'),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.H1('NBA 2013 dataset'),
    html.P('This is a dashboard to compare the players and the teams of the NBA 2013 season.'),
    html.H2('Dataset source'),
    convert_html_to_dash(__doc__),
    html.H2('Dataset description'),
    html.H3('Dataframe head'),
    convert_html_to_dash(df.head().to_html()),
    html.H3('Dataframe summary'),
    convert_html_to_dash(df.describe(include='all').to_html()),
    html.H2('Glossary'),
    convert_html_to_dash("""<table>
        <thead><tr><th>CODE</th><th>TEAM</th></tr></thead>
        <tbody>""" 
        + "".join([f"""<tr><td>{k}</td><td>{v}</td></tr>""" for k, v in dict_teams.items()]) 
        + """</tbody>
    </table>"""),
    html.H3('Variables'),
    convert_html_to_dash("""<table>
        <thead><tr><th>VARIABLE</th><th>DESCRIPTION</th></tr></thead>
        <tbody>""" 
        + "".join([f"""<tr><td>{k}</td><td>{v}</td></tr>""" for k, v in glossary.items()]) 
        + """</tbody>
    </table>""")
    ]
)

layout_players = html.Div([
    html.H1('Player Comparison'),
    html.H2('Choose the type of players you want to compare'),
    html.Div(dcc.Dropdown(id = 'player-dropdown',
                          options= [{'label': 'Rookies (under 24 yo)', 'value': 'rookies'},
                                    {'label': 'Seniors (over 24 yo)', 'value': 'seniors'}])),
    html.Div(dcc.Graph(id='page-1-graph')),
])

layout_teams = html.Div([
    html.H1('Team Comparison'),
    html.H2('Choose the statistic to compute'),
    html.Div(dcc.Dropdown(id='statistics-dropdown',
                          options=[{'label': v, 'value': k} for k, v in glossary.items() 
                                   if k in numerical_variables])),
    html.H2('If needed, split the analysis by position played'),
    html.Div(dcc.Slider(id = 'slider_1',
                      min = 0,
                      max = len(positions_played) - 1,
                      marks={index: str(positions[_]) for index, _ in enumerate(positions_played)},
                      step = None)),
    html.Div(dcc.Graph(id='page-2-graph')),
])


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/players':
        return layout_players
    elif pathname == '/teams':
        return layout_teams
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")