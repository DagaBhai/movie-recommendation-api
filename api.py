import pickle
import requests
from flask import Flask,render_template
from flask_restful import Api,Resource,reqparse,fields,marshal_with,abort
from dotenv import load_dotenv
import os

load_dotenv()
app=Flask(__name__)
api=Api(app)

movies = pickle.load(open('movies_list.pkl', 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
api_key=os.getenv("API_KEY")

def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    if 'poster_path' in data and data['poster_path']:
        poster_path = data['poster_path']
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Poster"
    
def recommend(movie_name):
    movie_matches = movies[movies['title'].str.lower() == movie_name.lower()]
    if movie_matches.empty:
        return None
    index = movies[movies['title'] == movie_name].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    for i in distance[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movie_id))
    print(recommend_movie,recommend_poster)
    return recommend_movie, recommend_poster

user_args = reqparse.RequestParser()
user_args.add_argument("movie",type=str,required=True,help="Movie name cannot be blank")

user_fields = {
    "movies_list": fields.List(fields.Nested({
        'movie_name': fields.String,
        'poster_link': fields.String 
    }))
}

class User(Resource):
    @marshal_with(user_fields)
    def post(self):
        args=user_args.parse_args() 
        movie_name=args["movie"].title()
        movie_list,movie_poster=recommend(movie_name)
        if not movie_list:
            abort(404,"no movie recommendations found")
        return {"movies_list":[
            {"movie_name":movie_list[0], "poster_link":movie_poster[0]},
            {"movie_name":movie_list[1], "poster_link":movie_poster[1]},
            {"movie_name":movie_list[2], "poster_link":movie_poster[2]},
            {"movie_name":movie_list[3], "poster_link":movie_poster[3]},
            {"movie_name":movie_list[4], "poster_link":movie_poster[4]}]
        }, 200

api.add_resource(User,"/api/movie_list")

@app.route("/")
def home():
    return render_template("index.html")
if __name__=="__main__":
    app.run(debug=True)
