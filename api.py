import pickle
import requests
from flask import Flask
from flask_restful import Api,Resource,reqparse,fields,marshal_with,abort

app=Flask(__name__)
api=Api(app)

movies = pickle.load(open('movies_list.pkl', 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))

def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=7e4b636e12f4a8277173702840ec1afb&language=en-US'
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

user_fields = {"mvoies_list":fields.Nested({
    'movie_1': fields.String,
    'movie_2': fields.String,
    'movie_3': fields.String,
    'movie_4': fields.String,
    'movie_5': fields.String
    }),
    "movies_poster_links":fields.Nested({
        'movie_1': fields.String,
        'movie_2': fields.String,
        'movie_3': fields.String,
        'movie_4': fields.String,
        'movie_5': fields.String
    })
}

class User(Resource):
    @marshal_with(user_fields)
    def post(self):
        args=user_args.parse_args() 
        movie_list,movie_poster=recommend(movie_name=args["movie"].title())
        if not movie_list:
            abort(404,"no movie recommendations found")
        return {"mvoies_list":{
            'movie_1': movie_list[0],
            'movie_2': movie_list[1],
            'movie_3': movie_list[2],
            'movie_4': movie_list[3],
            'movie_5': movie_list[4]},
            "movies_poster_links":{
            'movie_1': movie_poster[0],
            'movie_2': movie_poster[1],
            'movie_3': movie_poster[2],
            'movie_4': movie_poster[3],
            'movie_5': movie_poster[4]}
        }, 200

api.add_resource(User,"/api/movie_list")

@app.route("/")
def home():
    return "<h1>this is an flask application</h1>"

if __name__=="__main__":
    app.run(debug=True)
