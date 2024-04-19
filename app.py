# %%
#import dependencies
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import dash_bootstrap_components as dbc
from IPython.display import Image, display, Markdown


# %%
#read the dataset
df=pd.read_csv('data.csv')

# %%
#define external stylesheet
external_stylesheets = ['https://bootswatch.com/5/quartz/bootstrap.css']

# %%
#GENRE DISTRIBUTION STACKED BARCHART

#define genres for stacked bar chart
stacked_bar_chart_genres = [
    'Animation', 'Drama', 'Romantic', 'Comedy', 'Spy', 'Crime', 'Thriller',
    'Adventure', 'Documentary', 'Horror', 'Action', 'Western', 'Biography',
    'Sci-Fi', 'War'
]

#define years for slider marks (show every 10 years)
year_marks = {str(year): str(year) for year in range(df['year'].min()-1, df['year'].max()+1, 10)}

#BOXPLOT

#define genre options for boxplot
boxplot_genre_options = ['Romantic', 'Comedy', 'Crime', 'Drama', 'Horror', 'Action', 'Sci-Fi', 'Animation', 'Thriller']

#MOVIE CAROUSEL

#define image URLs
image_urls = [
    "https://www.paramountmovies.com/uploads/movies/null/kfm-pm-800x1200-c.jpg", #killers of the flower moon 
    "https://www.paramountmovies.com/uploads/movies/mission-impossible-dead-reckoning/mi-dr-final-key-art-c.jpg", #mission impossible 
    "https://www.oppenheimermovie.com/_nuxt/images/posters/two/full.a082ad.jpg", #oppenheimer 
    "https://media.themoviedb.org/t/p/w440_and_h660_face/uUbdc9TMwbazp1zCNzGtXoBHhUa.jpg", #barbie 
    "https://movies.universalpictures.com/media/kfp4-pw-poster-66147f5186e50-1.jpg", #kung fu panda
    "https://www.paramountmovies.com/uploads/movies/null/bobmarleyonelove-pm-800x1200-c.jpg", #bob marley
    "https://www.paramountmovies.com/uploads/movies/mean-girls-2024/meangirlstm-pm-800x1200-texted-c.jpg", #mean girls
]

#display images
for url in image_urls:
    display(Image(url=url, width=50, height=75))
    
#define a css style for the carousel container to resize images
carousel_style = {
    "width": "100%",  #width of the carousel should be 100% of its container
    "maxWidth": "350px",  #smaller max width set
    "margin": "auto",  #center the carousel horizontally
    "overflow": "hidden"  #hide any overflow (if images are larger than the container)
}

#adjust the style of each carousel item
carousel_items = [
    {
        "key": str(i),
        "src": url,
        "style": {"width": "100%", "height": "auto", "object-fit": "contain"}  
        #set width to 100% to ensure the image fills its container, height to auto to maintain aspect ratio
    } 
    for i, url in enumerate(image_urls, start=1)
]

#set a fixed height for the carousel
carousel_height = "250px"

#create a stylized title
title = html.H1("Trending Now", className="display-4 text-center text-white font-weight-bold mt-5")

#BUBBLE CHART

#define actors of interest
actors_of_interest = ['Adam Sandler', 'Chris Rock', 'Rob Schneider', 'Jackie Sandler',
                      'Steve Buscemi', 'Jennifer Aniston', 'Drew Barrymore', 'Kevin James',
                      'David Spade', 'Salma Hayek', 'Maya Rudolph',
                      'Allen Covert', 'Kevin Nealon', 'Nick Swardson']

#replace missing values with an empty string
df['actors'].fillna('', inplace=True)

#create a list to store dictionaries for each actor's aggregated ratings
actor_ratings = []

#iterate over each actor of interest and aggregate their ratings
for actor in actors_of_interest:
    actor_movies = df[df['actors'].apply(lambda x: actor in x)]
    public_vote_avg = actor_movies['public_vote'].mean()
    critics_vote_avg = actor_movies['critics_vote'].mean()
    actor_ratings.append({'actor': actor, 'public_vote_avg': public_vote_avg, 'critics_vote_avg': critics_vote_avg})

#convert the list of dictionaries into a dataframe
actor_ratings_df = pd.DataFrame(actor_ratings)

#create a list to store dictionaries for each actor's movie count
actor_movie_counts = []

#iterate over each actor of interest and count their movies
for actor in actors_of_interest:
    actor_movie_count = df['actors'].apply(lambda x: actor in x).sum()
    actor_movie_counts.append({'actor': actor, 'movie_count': actor_movie_count})

#convert the list of dictionaries into a dataframe
actor_movie_counts_df = pd.DataFrame(actor_movie_counts)

#merge actor_movie_counts with actor_ratings_df
actor_ratings_df = pd.merge(actor_ratings_df, actor_movie_counts_df, on='actor')

#calculate the scaling factor to adjust bubble sizes proportionately
max_movie_count = actor_ratings_df['movie_count'].max()
scaling_factor = 1000 / max_movie_count  #adjust number according to preference

#HEATMAP

#list of actors previously defined in bubblechart section

#filter the dataset to include only movies that involve at least one of the actors of interest
filtered_data = df[df['actors'].apply(lambda x: isinstance(x, str) and any(actor in x for actor in actors_of_interest))]

#create a matrix to count collaborations
collaboration_matrix = pd.DataFrame(0, index=actors_of_interest, columns=actors_of_interest)

#create a dictionary to store movie titles for each pair of actors
movies_dict = {}

#iterate through each movie and update collaboration matrix
for index, row in filtered_data.iterrows():
    movie_title = row['title']
    movie_actors = row['actors'].split(',')
    movie_actors = [actor.strip() for actor in movie_actors]  #remove leading/trailing whitespaces
    for i in range(len(movie_actors)):
        actor1 = movie_actors[i]
        if actor1 in actors_of_interest:
            for j in range(i + 1, len(movie_actors)):
                actor2 = movie_actors[j]
                if actor2 in actors_of_interest:
                    collaboration_matrix.at[actor1, actor2] += 1
                    collaboration_matrix.at[actor2, actor1] += 1  #since it's a symmetric matrix
                    #store movie title for this pair of actors
                    key = tuple(sorted([actor1, actor2]))  #sort actor names alphabetically
                    if key not in movies_dict:
                        movies_dict[key] = set()
                    movies_dict[key].add(movie_title)

#create a static heatmap with hover text and a custom pink colorscale
heatmap_data = go.Heatmap(
    z=collaboration_matrix.values,
    x=collaboration_matrix.columns,
    y=collaboration_matrix.index,
    colorscale=[[0, '#FCE4EC'], [0.25, '#F8BBD0'], [0.5, '#F48FB1'], [0.75, '#F06292'], [1, '#E91E63']],  #lightest to darkest pink
    zmin=0,
    hoverinfo='text',
    text=[[f'<b>{actor1}, {actor2}</b><br>' + ('<br>'.join([f'- {movie}' for movie in sorted(movies_dict.get(tuple(sorted([actor1, actor2])), []))]) if movies_dict.get(tuple(sorted([actor1, actor2]))) else 'No collaborations found') if actor1 != actor2 else f'<b>{actor1}</b><br>' + ('<br>'.join([f'- {movie}' for movie in sorted(movies_dict.get((actor1, actor1), []))]) if movies_dict.get((actor1, actor1)) else '') for actor2 in collaboration_matrix.columns] for actor1 in collaboration_matrix.index]
)

layout = go.Layout(
    title='Actor Collaborations Heatmap',
    xaxis=dict(tickfont=dict(color='white', size=12), automargin=True),  #customize x-axis tick font
    yaxis=dict(tickfont=dict(color='white', size=12), automargin=True),  #customize y-axis tick font
    paper_bgcolor='rgba(255, 255, 255, 0.01)', #transparent background
    font=dict(color='white', size=14, family='Bangers, sans-serif') #customize font for all text elements
)

#SCATTERPLOT

#define genres and options for dropdown menu
genres = [
    'Animation', 'Drama', 'Romantic', 'Comedy', 'Spy', 'Crime', 'Thriller',
    'Adventure', 'Documentary', 'Horror', 'Action', 'Western', 'Biography',
    'Musical', 'Sci-Fi', 'War', 'Fantasy'
]
scatter_genre_options = [{'label': genre, 'value': genre} for genre in genres]

#define colors for each genre
scatter_genre_colors = {
    'Animation': '#af7ac5',   
    'Drama': '#5499c7',     
    'Romantic': '#ff6f61',  
    'Comedy': '#8e44ad',      
    'Spy': '#e0115f',         
    'Crime': '#00ffff',     
    'Thriller': '#5d3fd3',     
    'Adventure': '#c39bd3',    
    'Documentary': '#7fb3d5',  
    'Horror': '#ff00ff',       
    'Action': '#d7bde2',    
    'Western': '#1f51ff',     
    'Biography': '#9b59b6', 
    'Musical': '#ff69b4',      
    'Sci-Fi': '#ffc0cb',      
    'War': '#000080',   
    'Fantasy': '#3498db'     
}

#define custom colors for each genre
genre_colors = {
    'Action': '#d7bde2',
    'Adventure': '#c39bd3',
    'Animation': '#af7ac5',
    'Biography': '#9b59b6',
    'Biblical': '#76448a',
    'Comedy': '#8e44ad',
    'Crime': '#a9cce3',
    'Documentary': '#7fb3d5',
    'Drama': '#5499c7',
    'Erotico': '#2980b9',
    'Fantasy': '#3498db',
    'Gangster': '#76d7c4',
    'Grotesque': '#de3163',
    'Horror': '#ff00ff',
    'Melo': '#ccccff',
    'Musical': '#ff69b4',
    'Mythology': '#ffb6c1',
    'Noir': '#da70d6',
    'Romantic': '#f8c8dc',
    'Sci-Fi': '#ffc0cb',
    'Short Movie': '#800080',
    'Sperimental': '#e30b5c',
    'Sport': '#f33a6a',
    'Spy': '#e0115f',
    'Stand-up Comedy': '#d8bfd8',
    'Super-hero': '#6495ed',
    'Thriller': '#5d3fd3',
    'War': '#000080',
    'Western': '#1f51ff'
}



# %%
#initialize dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#connect the server for render
server=app.server

# %%
#define layout components
navbar = html.Nav(
    className="navbar navbar-dark bg-primary",
    children=[
        html.A("Movie Search", className="navbar-brand"),
    ]
)

#adjust the style of the carousel component
carousel = html.Div([
    title,  #add the title above the carousel
    dbc.Carousel(
        items=carousel_items,
        controls=True,
        indicators=True,
        interval=1500,
        ride="carousel",
        style=carousel_style  #apply the css style to the carousel container
    )
], style={"margin": "auto", "text-align": "center", "margin-top": "0px", "margin-bottom": "20px"})


stacked_bar_chart = html.Div([
    html.H1("Distribution of Genres Over Time", style={'text-align': 'center'}),
    dcc.RangeSlider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        marks={str(year): {'label': str(year), 'style': {'color': 'white'}} for year in range(df['year'].min()-1, df['year'].max()+1, 10)},
        step=1,
    ),
    dcc.Graph(id='genre-graph')
], style={'width': '80%', 'margin': 'auto'})


scatterplot = html.Div([
    html.Link(
        rel='stylesheet',
        href='/Users/ciarafasullo/Desktop/DS4003/APP/assets/app_style.css'  #path to external stylesheet
    ),
    html.H1("Movie Duration vs Average Ratings"),
    dcc.Dropdown(
        id='genre-dropdown',
        options=scatter_genre_options,
        value='Animation', #default value to populate into graph
        multi=True, #allow multiple selections
        style={'width': '50%', 'color': 'hotpink'} #change text color to hot pink
    ),
    dcc.Graph(id='scatter-plot')
])

bubble_chart = html.Div([
    dcc.Graph(
        id='bubble-chart',
        figure={
            'data': [
                {
                    'x': actor_ratings_df['critics_vote_avg'],
                    'y': actor_ratings_df['public_vote_avg'],
                    'mode': 'markers',
                    'marker': {
                        'size': actor_ratings_df['movie_count'] * scaling_factor,  #adjust bubble sizes
                        'sizemode': 'area',
                        'sizeref': 2. * max(actor_ratings_df['movie_count']) / (10. ** 2),  #adjust reference size
                    },
                    'text': actor_ratings_df['actor'],
                }
            ],
            'layout': {
                'xaxis': {'title': 'Average Critics Vote', 'color': 'white', 'titlefont': {'color': 'white'}},
                'yaxis': {'title': 'Average Public Vote', 'color': 'white', 'titlefont': {'color': 'white'}},
                'hovermode': 'closest',
                'title': {
                    'text': 'Average Critic Ratings versus Average Public Ratings',
                    'font': {'color': 'white', 'family': 'Bangers'},
                    'x': 0.5  #centered title
                },
                'plot_bgcolor': 'rgba(255, 255, 255, 0.1)',  #transparent white background
                'paper_bgcolor': 'rgba(255, 255, 255, 0.01)',  #transparent white paper background
            }
        }
    )
])

boxplot = html.Div(style={'backgroundColor': 'rgba(255, 255, 255, 0.01)'}, children=[
    html.H1(
        children='Movie Ratings by Genre',
        style={
            'textAlign': 'center',
            'color': 'white',
            'fontFamily': 'Bangers'
        }
    ),
    dcc.Dropdown(
        id='genre-dropdown-boxplot',  
        options=[{'label': genre, 'value': genre} for genre in boxplot_genre_options],
        value=['Romantic'],  #set default value to romantic list for multi-select
        multi=True,  #enable multi-select
        style={'color': 'hotpink'}
    ),
    dcc.Graph(
        id='genre-boxplot',
        config={'displayModeBar': False}
    )
])

heatmap = html.Div([
    dcc.Graph(id='heatmap', figure={'data': [heatmap_data], 'layout': layout}),
])

description = html.Div([
html.Div([
    html.P("Our Movie Analytics Dashboard provides valuable insights into the world of cinema, leveraging a rich dataset sourced from FilmTV, a credible platform akin to IMDb. With over 40,000 movies from various countries, this dataset offers comprehensive coverage, making it an invaluable resource for movie enthusiasts and industry professionals alike.", style={'margin-bottom': '20px'}),
    html.P("This dataset pulls movie data from FilmTV, which is a credible source (similar to IMDb) that gathers data on various movies - whether that be their genre, actors, ratings, etc. FilmTV also features movies from an array of countries, providing us with data that is much more expansive than IMDb or other American websites.", style={'margin-bottom': '20px'}),
    html.P("This dataset was created to provide further information in regards to the aspects that make a movie successful from users or profit perspective. It was also designed to be able to be combined with other movie datasets publicly available through Rotten Tomatoes, IMDb, etc.", style={'margin-bottom': '20px'}),
    html.P("Source Information:", style={'font-weight': 'bold'}),
    html.P("FilmTV: https://www.filmtv.it/", style={'margin-bottom': '20px'}),
    html.P("Data Transformation History:", style={'font-weight': 'bold'}),
    html.P("The data has been scraped from the publicly available website https://www.filmtv.it/ and was last updated on 2023-10-21.", style={'margin-bottom': '20px'}),
    html.P("Authorship and Ownership (License):", style={'font-weight': 'bold'}),
    html.P("CC0: Public Domain", style={'margin-bottom': '20px'}),
    html.P("Dependencies:", style={'font-weight': 'bold'}),
    html.P("- Collection methodology: Python script (requests library)", style={'margin-bottom': '20px'}),
    html.P("Versioning:", style={'font-weight': 'bold'}),
    html.P("- Dataset is updated annually (last updated 2023-10-21)", style={'margin-bottom': '20px'}),
], style={'max-width': '800px', 'margin': 'auto'}),
], style={'textAlign': 'center', 'width': '100%', 'margin': '10px'}) #added width 100%

movie_dropdown_search = dcc.Dropdown(
    id='movie-dropdown-search',  
    options=[],  #options populate dynamically based on inputs
    placeholder='Enter movie title...',
    style={'width': '50%', 'color': 'hotpink'} #change text color to hot pink
)


# %%
#define app layout
app.layout = html.Div([
    #title
    html.Div(
        html.H1("MovieMate", style={'textAlign': 'center', 'color': 'white', 'fontFamily': 'Bangers'}),
        style={'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'overflow': 'hidden', 'width': '100%'}  #semi-transparent black background
    ),
    
    #movie search (spanning the entire width with additional vertical space)
    html.Div([
        html.Nav(
            className="navbar navbar-dark bg-primary",
            children=[
                html.A("Movie Search", className="navbar-brand"),
            ]
        ),
        dcc.Dropdown(
            id='movie-dropdown-search',  
            options=[],
            placeholder='Enter movie title...',
            style={'width': '100%', 'color': 'hotpink'} #change text color to hot pink
        ),
        html.Div(id='movie-info')
    ], style={'overflow': 'visible', 'width': '100%', 'margin-bottom': '5%'}),

    #carousel and stacked bar chart (both on the same row)
    html.Div([
        #carousel with margins on all sides
        html.Div(
            carousel,
            style={'float': 'left', 'width': '45%', 'overflow': 'hidden', 'margin-right': '10px', 'margin-left': '40px', 'margin-top': '60px', 'margin-bottom': '80px'}  #adjust margin-right, margin-left, margin-top, and margin-bottom for space between carousel and stacked bar chart, and margins on all sides of the carousel
        ),
        
        #stacked bar chart on the right
        html.Div(
            stacked_bar_chart,
            style={'float': 'right', 'width': '45%', 'overflow': 'hidden'}
        ),
    ], style={'overflow': 'hidden', 'width': '100%', 'margin': 'auto'}),  #center the row

    #scatterplot and bubble chart (both on the same row)
    html.Div([
        #scatterplot (taking up half of the width)
        html.Div(scatterplot, style={'float': 'left', 'width': '50%', 'overflow': 'hidden'}),
        
        #bubble chart (taking up the other half of the width)
        html.Div(bubble_chart, style={'float': 'left', 'width': '50%', 'overflow': 'hidden'}),
    ], style={'overflow': 'hidden', 'width': '100%'}),
    
    #boxplot and heatmap (both on the same row)
    html.Div([
        #boxplot (taking up half of the width)
        html.Div(boxplot, style={'float': 'left', 'width': '50%', 'overflow': 'hidden'}),
        
        # heatmap (taking up the other half of the width)
        html.Div(heatmap, style={'float': 'left', 'width': '50%', 'overflow': 'hidden'}),
    ], style={'overflow': 'hidden', 'width': '100%'}),
    
    #description (spanning the entire width)
    html.Div(description, style={'overflow': 'hidden', 'width': '100%'}),
])



# %%
#define callbacks

#callback to update scatterplot based on selected genres
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('genre-dropdown', 'value')]
)    
def update_plot(selected_genres):
    if not isinstance(selected_genres, list):
        selected_genres = [selected_genres]  #convert single value to list
    filtered_data = df[df['genre'].isin(selected_genres)]
    avg_vote = filtered_data.groupby(['duration', 'genre']).agg({'avg_vote': 'mean', 'title': 'first'}).reset_index()
    fig = px.scatter(avg_vote, x='duration', y='avg_vote', color='genre', hover_data=['title'], color_discrete_map=genre_colors)  #update color_discrete_map
    fig.update_layout(
        xaxis_title='Duration (minutes)', 
        yaxis_title='Average Rating',
        paper_bgcolor='rgba(255, 255, 255, 0.01)', #slightly transparent white background
        plot_bgcolor='rgba(255, 255, 255, 0.5)', #transparent white plot background
        font=dict(color='white', size=14, family='Bangers, sans-serif'), #change font and color of all text
        legend=dict(font=dict(color='white', size=12, family='Bangers, sans-serif')), #change font and color of legend text
        xaxis=dict(tickfont=dict(color='white', size=12, family='Bangers, sans-serif')), #change font and color of x-axis tick labels
        yaxis=dict(tickfont=dict(color='white', size=12, family='Bangers, sans-serif')) #change font and color of y-axis tick labels
    )
    return fig

#define callback to update movie dropdown options
@app.callback(
    Output('movie-dropdown-search', 'options'),  
    [Input('movie-dropdown-search', 'search_value')]
)
def update_dropdown_options(search_value):
    if search_value is None:
        return []
    else:
        filtered_options = df[df['title'].str.contains(search_value, case=False)]['title'].tolist()
        return [{'label': option, 'value': option} for option in filtered_options]
        
#define callback to update movie information
@app.callback(
    Output('movie-info', 'children'),
    [Input('movie-dropdown-search', 'value')]  
)
def update_movie_info(selected_movie):
    if selected_movie is None:
        return html.Div()
    else:
        movie_data = df[df['title'] == selected_movie].iloc[0]
        movie_title = movie_data['title']
        movie_year = movie_data['year']
        movie_genre = movie_data['genre']
        movie_description = movie_data['description']
        
        return html.Div([
            html.H2(movie_title),
            html.H3(f"Year: {movie_year}"),
            html.H3(f"Genre: {movie_genre}"),
            html.P(f"Description: {movie_description}")
        ])
    
#define callback to update boxplot based on selected genres
@app.callback(
    Output('genre-boxplot', 'figure'),
    [Input('genre-dropdown-boxplot', 'value')]
)
def update_boxplot(selected_genres):
    if not selected_genres:
        return {}

    filtered_data = df[df['genre'].isin(selected_genres)]
    fig = px.box(filtered_data, x='genre', y='avg_vote', title='Boxplot of Movie Ratings for Selected Genres')

    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 0.01)',
        paper_bgcolor='rgba(255, 255, 255, 0.25)',
        font=dict(color='white'),
        xaxis_title='Genre',  #update x-axis title
        yaxis_title='Average Rating'  #update y-axis title
    )

    return fig

@app.callback(
    Output('genre-graph', 'figure'),
    [Input('year-slider', 'value')]
)
def update_graph(selected_years):
    try:
        filtered_df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
        genre_counts = filtered_df.groupby(['year', 'genre']).size().unstack(fill_value=0)

        #use the condensed list of genres for the bar chart
        stacked_bar_chart_genres = ['Animation', 'Drama', 'Comedy', 'Thriller',
                                     'Adventure', 'Documentary', 'Horror', 'Action', 'Western',
                                     'Musical', 'Sci-Fi', 'War', 'Fantasy']
        
        traces = []
        for genre in stacked_bar_chart_genres:
            traces.append(go.Bar(
                x=genre_counts.index,
                y=genre_counts[genre],
                name=genre,
                marker_color=genre_colors.get(genre,'#7f7f7f')
            ))

        layout = go.Layout(
            barmode='stack',
            xaxis={'title': 'Year'},
            yaxis={'title': 'Number of Movies'},
            plot_bgcolor='rgba(255,255,255,0.5)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(color='white', size=14, family='Bangers, sans-serif') #customize font for all text elements
        )

        return {'data': traces, 'layout': layout}
    except Exception as e:
        print(e)
        return {'data': [], 'layout': {}}




# %%
#run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8063)

# %%
app.run(jupyter_mode="external")

