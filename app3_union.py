import requests
import pandas as pd
import pickle
import streamlit as st
import time

st.set_page_config(layout="wide")

# TMDb API Key
API_KEY = '9aba39119c399b5f3985ab6825be0aff'
REGION = 'IT'  # Modifica per la tua regione

# Carica i dati delle piattaforme di streaming dal CSV
providers_movies_df = pd.read_csv('providers_movies.csv')

# Carica i dati dei film e la matrice di similarità
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Funzione per ottenere il poster del film e il link alla scheda del film su TMDb
def fetch_poster_and_link(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
        response.raise_for_status()  # Controlla se la richiesta ha avuto successo
        data = response.json()
        poster_url = f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        movie_link = f"https://www.themoviedb.org/movie/{movie_id}"
        return poster_url, movie_link
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero del poster e del link per il film ID {movie_id}: {e}")
        return None, None

# Funzione per ottenere i film disponibili su una o più piattaforme dal CSV
def get_movies_by_providers_cached(provider_ids):
    if not provider_ids:
        return set()
    filtered_df = providers_movies_df[providers_movies_df['Provider'].isin([k for k, v in provider_mapping.items() if v in provider_ids])]
    return set(filtered_df['Movie ID'].unique())

# Funzione di raccomandazione
def recommend(movie, provider_ids=None):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]  # Esclude il film stesso
    
    if provider_ids:
        platform_movie_ids = get_movies_by_providers_cached(provider_ids)
    else:
        platform_movie_ids = set()  # Nessun filtro se non è specificato il provider
    
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_links = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        if not provider_ids or movie_id in platform_movie_ids:
            poster, link = fetch_poster_and_link(movie_id)
            if poster and link:
                recommended_movies.append(movies.iloc[i[0]].title)
                recommended_movies_posters.append(poster)
                recommended_movies_links.append(link)
                if len(recommended_movies) == 5:
                    break

    return recommended_movies, recommended_movies_posters, recommended_movies_links

# Interfaccia Streamlit
st.markdown("<h1 style='text-align: center;'>Movie Recommender System</h1>", unsafe_allow_html=True)

# Seleziona un film dall'elenco
cols = st.columns([1, 2, 4, 2, 1])  # Adatta le proporzioni come necessario
with cols[2]:
    selected_movie_name = st.selectbox('Inserisci un film che ti è piaciuto', movies['title'].values)

    # Seleziona una o più piattaforme di streaming
    platforms = st.multiselect('Seleziona una o più piattaforme di streaming', ['Netflix', 'Disney+', 'Amazon Prime','Apple tv','Tim vision'])
    provider_mapping = {'Netflix': 8, 'Disney+': 337, 'Amazon Prime': 119, 'Apple tv': 2,'Tim vision': 109}  # Mappatura ID provider aggiornata
    selected_provider_ids = [provider_mapping[platform] for platform in platforms]

st.markdown("""
<style>
div.stSpinner {
    text-align: center;
    align-items: center;
    justify-content: center;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)

# Creazione di più colonne per il layout
cols2 = st.columns([1, 5, 4, 2, 1])  # Adatta le proporzioni come necessario
cols3 = st.columns([1, 2, 4, 2, 1])  # Adatta le proporzioni come necessario

with cols2[2]:  # Colonna centrale per il pulsante e lo spinner
    button_clicked = st.button('Consiglia')

    if button_clicked:
        names, posters, links = recommend(selected_movie_name, selected_provider_ids)


if button_clicked and names:
    cols = st.columns(len(names), gap="large")  # Crea colonne per ogni film
    for i in range(len(names)):
        with cols[i]:
            st.markdown(f"<h3 style='text-align: center; font-size: 18px;'>{names[i]}</h3>", unsafe_allow_html=True)
            st.image(posters[i], width=250)  # Imposta la larghezza desiderata
            button_html = f"""
                <div style='text-align: center;'>
                    <a href='{links[i]}' target='_blank'>
                        <button style='padding: 5px; border-radius: 5px; border: none; cursor: pointer;'>
                            Informazioni aggiuntive
                        </button>
                    </a>
                </div>
            """
            st.markdown(button_html, unsafe_allow_html=True)

