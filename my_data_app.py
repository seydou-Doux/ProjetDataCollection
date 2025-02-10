import streamlit as st
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Mon Appli Streamlit",
    page_icon="https://i.ytimg.com/vi/04SzGXlIwSA/maxresdefault.jpg",
    layout="wide"
)

# CSS pour l’image de fond et le texte en blanc
st.markdown(
    """
    <style>
        .stApp {
            background: url("https://i.ytimg.com/vi/04SzGXlIwSA/maxresdefault.jpg") no-repeat center center fixed;
            background-size: cover;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: black !important;
            
        }
        .title {
            color: blue !important;
            font-weight: bold;
            font-size: 36px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">Bienvenue sur mon application Streamlit !</h1>', unsafe_allow_html=True)
st.write("Vous pouvez visualiser et télecharger des données")

# Dictionnaire des sites disponibles pour le scraping
sites_disponibles = {
    "Categorie Chien": "https://sn.coinafrique.com/categorie/chiens",
    "Categorie Mouton": "https://sn.coinafrique.com/categorie/moutons",
    "Categorie Lapin et Pigeon": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
    "Categorie Autres": "https://sn.coinafrique.com/categorie/autres-animaux"
}

# Fonction pour charger et afficher les données
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Le fichier {file_path} est introuvable.")
        return pd.DataFrame()


def display_data(file_path, title):
    """Affiche un bouton permettant de cacher ou afficher les données."""
    data = load_data(file_path)

    if data.empty:
        return
    
    show_data = st.checkbox(f"Afficher {title}", value=False)
    
    if show_data:
        st.subheader(title)
        st.write(f'Dimension des données : {data.shape[0]} lignes et {data.shape[1]} colonnes.')
        st.dataframe(data)

# Charger les données
display_data('data/donne-cat-autre.csv', 'Autres animaux')
display_data('data/donne_cat_chiens .csv', 'Chiens')
display_data('data/donne-cat-lapin-pigeon.csv', 'Lapin et Pigeon')
display_data('data/donne-cat-moutons.csv', 'Moutons')

# Fonction de scraping
def site_a_scraper(url, num_pages):
    """Scrape les données du site spécifié pour le nombre de pages donné."""
    df = pd.DataFrame()

    try:
        for p in range(1, num_pages + 1):
            page_url = f"{url}?page={p}"
            res = get(page_url)
            soup = bs(res.text, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')

            data = []
            for container in containers:
                try:
                    url_container = container.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                    full_url = 'https://sn.coinafrique.com' + url_container
                    res_c = get(full_url)
                    soup_c = bs(res_c.text, 'html.parser')

                    nom = soup_c.find('span', class_='breadcrumb cible').text.strip()
                    prix = soup_c.find('p', class_='price').text.replace(' ', '').replace('CFA', '').strip()
                    adresse = soup_c.find_all('span', class_='valign-wrapper')[1].text.strip()

                    img_tag = soup_c.find('div', class_='swiper-wrapper')
                    img_link = img_tag.div['style'].split('(')[-1].strip(')') if img_tag else ''

                    data.append({'Nom': nom, 'Prix': prix, 'Adresse': adresse, 'Image': img_link})

                except Exception as e:
                    st.warning(f"Erreur sur une annonce : {e}")

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)

    except Exception as e:
        st.error(f"Erreur lors du scraping : {e}")
    
    return df

# Barre latérale pour la navigation
st.sidebar.title("Menu de navigation")
menu = st.sidebar.radio(
    "Choisissez une section :",
    options=["Scraping",  "Tableau de Bord","Formulaire d'Évaluation"]
)

# Section Scraping
if menu == "Scraping":
    st.header("Scraping Immobilier")

    site_choisi = st.selectbox("Choisissez un site à scraper :", options=list(sites_disponibles.keys()))
    nombre_pages = st.slider("Nombre de pages à scraper :", min_value=1, max_value=20, value=1)

    if st.button("Lancer le scraping"):
        st.info(f"Scraping en cours pour {site_choisi} ({nombre_pages} pages)...")
        url = sites_disponibles[site_choisi]
        resultat = site_a_scraper(url, nombre_pages)

        if not resultat.empty:
            st.success("Scraping terminé avec succès !")
            st.data_editor(resultat, hide_index=True)

            csv = resultat.to_csv(index=False).encode('utf-8')
            st.download_button("Télécharger les données en CSV", csv, "resultats_scraping.csv", "text/csv")
        else:
            st.warning("Aucune donnée récupérée.")

# Section Formulaire d'Évaluation
if menu == "Formulaire d'Évaluation":
    st.header("Formulaire d'évaluation de l'application")
    st.write("Merci de bien vouloir remplir le formulaire pour nous aider à améliorer notre application.")
    st.markdown("[Cliquez pour renseigner le formulaire](https://ee.kobotoolbox.org/x/z9JJ143d)")


def get_data(Categories_Animaux):
    if Categories_Animaux == "Moutons":
        return pd.read_csv("data/donne_mouton_nettoyer.csv")
    elif Categories_Animaux == "Chiens":
        return pd.read_csv("data/donne_chien_nettoyer.csv")
    elif Categories_Animaux == "Poules Pigeons Lapins":
        return pd.read_csv("data/donne_lapi_nettoyer.csv")
    elif Categories_Animaux == "Autres":
        return pd.read_csv("data/donne_autre_nettoyer.csv")

# Section Tableau de Bord
if menu == "Tableau de Bord":
    st.header('📊 Tableau de Bord ')

    # Sélectionner le type de bien
    type_bien = st.selectbox("Catégorie d'Animaux", ["Moutons", "Chiens", "Poules Pigeons Lapins", "Autres"])
    
    data = get_data(type_bien)  # Chargement des données

    # Vérification que les données sont disponibles
    if data.empty:
        st.warning("Aucune donnée disponible pour cette catégorie.")
    else:
        # Diagramme des Adresses
        if st.checkbox('📍 Afficher le diagramme des Adresses'):
            st.subheader('Distribution des Adresses')
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.countplot(x='adresse', data=data, palette="viridis")
            ax.set_xlabel('Adresse')
            ax.set_ylabel('Nombre d\'annonces')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Moyenne des Prix par Adresse
        if st.checkbox('💰 Afficher la moyenne des prix par adresse'):
            st.subheader('Moyenne des Prix par Adresse')
            mean_prices = data.groupby('adresse')['prix'].mean().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x='adresse', y='prix', data=mean_prices.sort_values(by='prix', ascending=False), palette="viridis")
            ax.set_xlabel('Adresse')
            ax.set_ylabel('Moyenne des Prix')
            plt.xticks(rotation=45)
            st.pyplot(fig)


