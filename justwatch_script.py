import requests
import pandas as pd
import pickle

# TMDb API Key
API_KEY = '9aba39119c399b5f3985ab6825be0aff'
REGION = 'IT'  # Modifica per la tua regione

provider_mapping = {'Netflix': 8, 'Disney+': 337, 'Amazon Prime': 119, 'Apple tv': 2, 'Tim vision': 109}

def get_movies_by_providers(provider_ids):
    all_movies = {}
    for provider_id in provider_ids:
        movies_set = set()
        page = 1
        while True:
            try:
                url_movies = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_watch_providers={provider_id}&watch_region={REGION}&page={page}"
                response = requests.get(url_movies)
                response.raise_for_status()
                data = response.json()
                movies = data.get('results', [])
                if not movies:
                    break
                movies_set.update(movie['id'] for movie in movies)
                page += 1
                if page > 300:
                    break
            except requests.exceptions.RequestException as e:
                print(f"Errore nel recupero dei film per il provider ID {provider_id}: {e}")
                break
        all_movies[provider_id] = list(movies_set)
    return all_movies

def save_to_csv(all_movies, provider_mapping):
    rows = []
    for provider_id, movie_ids in all_movies.items():
        provider_name = [name for name, pid in provider_mapping.items() if pid == provider_id][0]
        for movie_id in movie_ids:
            rows.append({'Provider': provider_name, 'Movie ID': movie_id})
    df = pd.DataFrame(rows)
    df.to_csv('providers_movies.csv', index=False)
    print("Dati delle piattaforme di streaming salvati in 'providers_movies.csv'.")

if __name__ == "__main__":
    provider_ids = list(provider_mapping.values())
    all_movies = get_movies_by_providers(provider_ids)
    save_to_csv(all_movies, provider_mapping)
