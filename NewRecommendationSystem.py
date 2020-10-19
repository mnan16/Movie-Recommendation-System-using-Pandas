# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 16:13:48 2020

@author: mehul
"""

#Importing Libraries
import pandas as pd
        

#Importing Data into DataFrame
movies= pd.read_csv('Movies.dat', sep='::', header= None, names= ['MovieId', 'Title', 'Genre'] )
ratings= pd.read_csv('Ratings.dat', sep='::', header=None, names= ['UserId', 'MovieId', 'Rating', 'Timestamp'])

#Extract Year from Title
movies['Year']=movies['Title'].str.extract(r'\((\d{4})\)')
movies['Year']=pd.to_datetime(movies['Year'], format="%Y")
movies['Year']=movies['Year'].dt.year

#Have Title include only movie name
movies['Title']= movies['Title'].str[:-7]

'''Get list of all users that have rated given movie id.
The function takes a movie_id as input and provides the user_id of all users that have rated this movie_id 
with their respective rating.
'''
def get_list_of_users(movie_id):
    ulist=ratings.loc[ratings['MovieId']==movie_id,['UserId','Rating']].reset_index().drop(columns={'index'})
    return ulist

user_list=get_list_of_users(1)
len(user_list)

'''Get list of movies rated by user id
The function takes a user_id as input and provides the movie_id of all movies that have been rated by this user_id.
'''
def get_list_of_movies(user_id):
    mlist=ratings.loc[ratings['UserId']==user_id,'MovieId'].sort_values().reset_index().drop(columns={'index'})
    return mlist

movie_list=get_list_of_movies(3)


'''
Get list of movies rated by user id.
The function takes a user_id as input and provides the title of all movies that have been rated by this user_id.
'''
def get_list_of_movies_with_title(user_id):
    mlist=ratings.loc[ratings['UserId']==user_id,'MovieId']
    mlist1=movies.loc[movies['MovieId'].isin(mlist),'Title']
    return mlist1

movie_list_with_title=get_list_of_movies_with_title(3)

'''
Get list of movies that released in a specific year.
The function takes a year as inpur and returns the movie_id, title and genre of all movies that released in that year.
'''
def get_movie_from_year(year):
    mlist=movies.loc[movies['Year']==year,['MovieId','Title','Genre']].reset_index().drop(columns={'index'})
    return mlist

movies_in_year=get_movie_from_year(1919)


'''
Get list of movies that have been rated by more than 'x' users.
This function can be super useful as it provides valuable insight regarding which movies are popular.
High number of user ratings for a movie indicates high popularity.

This function can also be used when recommending movies to users. 
Higher number of user ratings can be translated to more appropriate ratings for a movie.
(If a movie has been rated by just one person, it makes the rating heavily skewed)

The function returns a dataframe that has the title and genre of movies.
'''
def get_movies_rated_more_than(val):
    count=ratings.groupby('MovieId').size()
    mids=count[count>val].index.values.tolist()
    mlist=movies.loc[movies['MovieId'].isin(mids),['Title','Genre']]
    return mlist

movies_rated_more_than=get_movies_rated_more_than(2800)

'''Find average rating for every "Genre" movie
Genre refers to values such as Action, Adventure, Comedy, etc. found in the movies dataframe.
The functions get_movid_by_genre() and get_df_by_genre() help accomplish this task.
'''

'''Get list of movie id's for a specific genre

The function has the following arguments: 
Movies: The dataframe for filtering movies by genre.
Genre: The required genre.

The function returns:
Movid: List of movie id's that have the respective genre.
'''
def get_movid_by_genre(movies,genre):
    movid=[]
    for i in range(len(movies.index)):
        mid,gen=movies.loc[i,['MovieId','Genre']]
        gt=gen.split('|')
        if genre in gt:
            movid.append(mid)
    return movid


'''Get Title, Movie Id and Genre of movies for a specific genre

This function has the following arguments:
Movies: The dataframe for filtering movies by genre.
Genre: The required genre.

The function returns:
Rmavg: Dataframe containing title, movie id and genre of movies for respective genre. Dataframe is sorted based on movie_id.
'''
def get_df_by_genre(movies,genre):
    movid=get_movid_by_genre(movies,genre)
    rmovs=ratings.loc[ratings['MovieId'].isin(movid),['MovieId','Rating']].sort_values(by='MovieId')
    rmavg=pd.DataFrame(rmovs.groupby('MovieId')['Rating'].mean()).reset_index().rename(columns={'index':'MovieId'})
    rmavg=pd.merge(rmavg,pd.DataFrame(movies[['MovieId','Title']]), on='MovieId')
    rmavg.set_index('Title',inplace=True)
    return rmavg

movie_list_for_genre=get_df_by_genre(movies,"Romance")

'''
Get list of movies that released in a specific year of a paritcular genre
The function has the following parameters:
Year: The year when the movie released.
Genre: The genre of the movie.

The function returns:
movie_with_year_genre: Dataframe containing title, movie id and genre of movies for respective genre. Dataframe is sorted based on movie_id.
'''
def get_list_of_movies_with_year_and_genre(year,genre):
    miy=get_movie_from_year(year)
    movie_with_year_genre=get_df_by_genre(miy,genre)
    return movie_with_year_genre

movie_with_year_genre=get_list_of_movies_with_year_and_genre(1919,'Drama')

'''List of All genres

The function retruns:
A list that contains all the genres present in the MovieLens dataset. This list is sorted alphabetically.
'''
def get_all_genres():
    gen=movies.loc[:,'Genre']
    gen_list=[]
    for i in gen:
        gt=i.split('|')
        for j in gt:
            if j in gen_list:
                continue
            else:
                gen_list.append(j)
    return sorted(gen_list)

'''Average rating given by UserId for each Genre.

Each user has genres that they have rated by watching movies that belong to this genre.
There may also be genres that the user has never rated as the user has not watched any movies that belong to this genre.

The function has the following arguments:
Uid: User id of the user.

The function returns:
Uavgr: Series with average rating provided by user for each genre. Genre is the index for this Series.
nan values indicate that the user has never rated a movie of this genre.
'''
def get_avg_genre_rating_by_user(uid):
    g=ratings.loc[ratings['UserId']==uid,['MovieId','Rating']]
    g=pd.merge(g,pd.DataFrame(movies[['MovieId','Genre']]),on='MovieId')
    gen_list=get_all_genres()
    uavgr=pd.Series()
    for i in gen_list:
        uavgr[i]= g.loc[g['Genre'].str.contains(i),'Rating'].mean()
    uavgr.name='UserId '+ str(uid)
    return uavgr

user_avg_rating_for_genre=get_avg_genre_rating_by_user(1)

'''Recommend movies to user from Genres the user has never rated.
A good application for any recommendation system is to introduce users to novel content.
With this function, we are trying to recommend movies to a user for genres that the user has never rated.

The function has the following arguments:
Uid: User id of a user.

The function returns:
Ngmovs: Dataframe with the top 10 movies for each genre that the user has never rated.
Top 10 movies for each genre are decided based on the ratings provided by other users.
'''
def movies_from_new_genre(uid):
    uavgr=get_avg_genre_rating_by_user(uid)
    ungen=uavgr[uavgr.isnull()].index.tolist()
    ngmovs=pd.DataFrame()
    for genre in ungen:
        rt= get_df_by_genre(movies,genre).sort_values(by='Rating',ascending=False)
        mlist=rt.head(10).index.values.tolist()
        ngmovs[genre]=mlist
    return ngmovs

new_genre_movies=movies_from_new_genre(1)    

'''Recommend movies from Genres that the user has rated
Another good application for any recommendation system is to recommend movies of genres that the user has rated.
These movies may belong to the genre that the user has seen movies from but the user has never seen these movies.

The function has the following arguments:
Uid: User id of a user.

The function returns:
Ngmovs: Dataframe with the top 10 movies for each genre that the user has rated. These are movies that user has never seen.
Top 10 movies for each genre are decided based on the ratings provided by other users.
'''

def movies_from_same_genre(uid):
    g=ratings.loc[ratings['UserId']==uid,'MovieId']
    indexes=movies[movies['MovieId'].isin(g)].index.values.tolist()
    m=movies.drop(indexes).reset_index().drop(columns={'index'})
    uavgr=get_avg_genre_rating_by_user(uid)
    gen=uavgr[uavgr.isnull()==False].index.tolist()
    ngmovs=pd.DataFrame()
    for genre in gen:
        rt=get_df_by_genre(m,genre).sort_values(by='Rating',ascending=False)
        mlist=rt.head(10).index.values.tolist()
        ngmovs[genre]=mlist
    return ngmovs

new_movies=movies_from_same_genre(1)
