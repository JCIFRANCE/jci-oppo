import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------- CONFIGURATION ----------
st.set_page_config(
    page_title="Cartographie des opportunités",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS ----------
def setup_css():
    st.markdown("""
        <style>
            div[data-testid="stSliderTickBarMin"],
            div[data-testid="stSliderTickBarMax"],
            section[data-testid="stSidebar"] .stSlider label,
            section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"],
            section[data-testid="stSidebar"] .stSlider div[role="tooltip"],
            section[data-testid="stSidebar"] .stSlider span {
                display: none !important;
            }
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3,
            section[data-testid="stSidebar"] h4 {
                margin-top: 0rem !important;
                margin-bottom: 0rem !important;
            }
            /* Réduction de l’espace en haut du volet de sélection */
        section[data-testid="stSidebar"] .css-1d391kg {
            padding-top: 3rem !important;
        }
        /* Réduction du padding top au tout début de la page */
        .block-container {
            padding-top: 3rem !important;
        }
        /* Largeur initiale de la sidebar à 35% */
        section[data-testid="stSidebar"] {
            width: 35%;
        }
        
        </style>
    """, unsafe_allow_html=True)

# ---------- CHARGEMENT DES DONNÉES ----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/147E7GhixKkqECtBB1OKGqSy_CXt6skrucgHhPeU0Dog/export?format=csv"
    df = pd.read_csv(url, encoding="utf-8")
    df.columns = df.columns.str.strip().str.capitalize()
    df["Forme"] = df["Forme"].str.strip().str.capitalize().replace({
        "Autre": "Événement",
        "Evenement": "Événement",
        "Formation /atelier": "Formation",
        "Initiative /programme": "Programme",
        "Initiative/programme": "Programme"
    })
    df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])
    return df

# ---------- DICTIONNAIRES UTILES ----------
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪", "Concours": "🥇", "Projet": "🛠️",
    "Fonction": "👔", "Equipe": "🤝", "Événement": "🎫", "Formation": "🎓"
}

verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
verbe_icons = {
    "Apprendre": (
        "<span style='background-color: #026587; color: white; padding: 2px 6px; border-radius: 4px;'>Apprendre</span>",
        "#026587",
        "Apprendre"
    ),
    "Célébrer": (
        "<span style='background-color: #ED813D; color: white; padding: 2px 6px; border-radius: 4px;'>Célébrer</span>",
        "#ED813D",
        "Célébrer"
    ),
    "Responsabiliser": (
        "<span style='background-color: #D72D73; color: white; padding: 2px 6px; border-radius: 4px;'>Prendre des responsabilités</span>",
        "#D72D73",
        "Prendre des responsabilités"
    ),
    "Rencontrer": (
        "<span style='background-color: #5DB23C; color: white; padding: 2px 6px; border-radius: 4px;'>Se rencontrer</span>",
        "#5DB23C",
        "Se rencontrer"
    )
}

descriptions_verbes = {
    "Apprendre": "se former, monter en compétence et grandir",
    "Célébrer": "fêter les réussites, marquer les jalons, garder du temps pour le plaisir",
    "Responsabiliser": "prendre le lead, transmettre, coacher",
    "Rencontrer": "se faire des amis, réseauter, se réunir autour d'une table"
}
pilier_icons = {
    "Individu": (
        "<span style='background-color: #555DBE; color: white; padding: 2px 6px; border-radius: 4px;'>Individu en progression</span>",
        "#555DBE",
        "Individu en progression"
    ),
    "Entreprise": (
        "<span style='background-color: #484848; color: white; padding: 2px 6px; border-radius: 4px;'>Esprit d'Entreprise</span>",
        "#484848",
        "Esprit d'Entreprise"
    ),
    "Communaute": (
        "<span style='background-color: #80B7A4; color: white; padding: 2px 6px; border-radius: 4px;'>Service à la Communauté</span>",
        "#80B7A4",
        "Service à la Communauté"
    ),
    "Cooperation": (
        "<span style='background-color: #E3BD60; color: white; padding: 2px 6px; border-radius: 4px;'>Coopération Internationale</span>",
        "#E3BD60",
        "Coopération Internationale"
    )
}

descriptions_piliers = {
    "Développement individuel": "Savoir-être, développement personnel, outils du citoyen responsable, défense des valeurs, éthique",
    "Entreprise": "Savoir-faire, compétences de management, réseau business, tester ses idées",
    "Communaute": "Au service du territoire et de l’intérêt général, benchmark des actions, agir pour construire un monde meilleur",
    "Cooperation": "dépasser les horizons, diplomatie internationale, interculturalité, construire des projets inter-organisations"
}

# ---------- SLIDERS PERSONNALISÉS ----------
def afficher_sliders_personnalises(titre, description, data_dict, desc_dict, prefix):
    st.sidebar.markdown(f"<div style='font-size: 18px; font-weight: bold;'>{titre}</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<span style='font-size: 14px; color: grey;'>{description}</span>", unsafe_allow_html=True)
    valeurs = {}
    for k, (html_label, color, raw_label) in data_dict.items():
        st.sidebar.markdown(f"""
<div style='margin-bottom: 0.4rem;'>
  {html_label}
  <span style='font-weight: 300; font-size: 13px; color: grey;'> : {desc_dict.get(k, '')}</span>
</div>
""", unsafe_allow_html=True)
        valeurs[k] = st.sidebar.slider("", 0, 100, 25, key=f"{prefix}_{k}", label_visibility="collapsed")
    return valeurs

def score(row, prefs_eng, prefs_pil):
    s_eng = sum((row.get(k, 0) - prefs_eng[k])**2 for k in prefs_eng)
    s_pil = sum((row.get(k, 0) - prefs_pil[k])**2 for k in prefs_pil)
    return (s_eng + s_pil)**0.5

def make_visual(row, niveau_labels, small=False):
    piliers_labels = list(pilier_icons.keys())
    labels_piliers = [pilier_icons[p][2] for p in piliers_labels]  # pour hover
    couleurs_piliers = [pilier_icons[p][1] for p in piliers_labels]


    verbes_labels = list(verbe_map.keys())
    couleurs_verbes = [verbe_icons[v][1] for v in verbes_labels]

    fig = go.Figure()

    # 🎯 Cercle intérieur = piliers
    fig.add_trace(go.Pie(
        values=[row.get(p, 0) for p in piliers_labels],
        labels=labels_piliers,
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        showlegend=False,
        hovertemplate='<b>%{label}</b><extra></extra>',
        textposition='none'
    ))

    # 🔵 Cercle extérieur = verbes
    valeurs_verbes = [(row.get(k, 0), verbe_map[k], verbe_icons[k][1]) for k in verbe_map if row.get(k, 0) > 0]
    if valeurs_verbes:
        v, l, c = zip(*valeurs_verbes)
        fig.add_trace(go.Pie(
            values=v,
            labels=l,
            marker=dict(colors=c),
            hole=0.6,
            domain={'x': [0, 1], 'y': [0, 1]},
            textinfo='none',
            showlegend=False,
            hovertemplate='<b>%{label}</b><extra></extra>',
            textposition='none'
        ))

    # 🏷️ Niveaux au centre
    if not small:
        for i, n in enumerate(row["Niveau"]):
            fig.add_annotation(
                text=niveau_labels.get(n, n),
                x=0.5,
                y=0.5 - i * 0.09,
                showarrow=False,
                font=dict(size=11)
            )

    fig.update_layout(
        margin=dict(t=5, b=5, l=5, r=5),
        height=260 if not small else 180
    )
    return fig



def formatter_description(row, afficher_niveau=False):
    forme = row.get("Forme", "")
    description = row.get("Description", "Petite explication de l'opportunité")
    url = row.get("Url", "")
    niveau = ", ".join([niveau_labels.get(n, n) for n in row.get("Niveau", [])]) if afficher_niveau else ""
    
    contenu = f"{forme} – {description}"
    
    if pd.notna(url) and url.strip() != "":
        contenu += f" <a href='{url}' target='_blank' style='color: #007BFF;'>[🔗 plus d’infos ici]</a>"

    if afficher_niveau and niveau:
        contenu += f" <span style='color: grey;'>({niveau})</span>"
    
    return f"<div style='font-size:14px; color: #444; margin-top: -4px;'>{contenu}</div>"

# ---------- LANCEMENT APP ----------
setup_css()
df = load_data()

st.markdown("""
<div style='margin-bottom: 0rem;'>
  <h1 style='margin-bottom: 0rem;'>La cartographie des opportunités de la Jeune Chambre ... en Donuts 🍩</h1>
  </div>
<div style='font-size: 22px; line-height: 1; color: #333; margin-bottom: 0.5rem;'>
Chaque opportunité est une recette différente : découvre tes donuts de l’engagement, selon tes goûts et ton style !
</div>

<div style='font-size: 15px; line-height: 1.6; color: #333; margin-bottom: 2rem;'>
<b>ÉTAPE 1️⃣ Choisis tes ingrédients</b> : glisse les curseurs du volet à gauche pour créer une recette à ton image<br>
<b>ÉTAPE 2️⃣ Découvre ton assortiment gourmand de 9 donuts</b> : l’anneau extérieur révèle tes préférences d’engagement, l’anneau intérieur les domaines que tu veux nourrir. <br>
<b>ÉTAPE 3️⃣ Renseigne-toi et affine</b> : explore les détails, partage tes résultats, et profite du plaisir de l'engagement 😋
</div>

""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------
st.sidebar.markdown("## Crée ton propre mix : à toi de doser !")

pref_engagements = afficher_sliders_personnalises(
    "💓 Ce qui me fait vibrer c'est ...",
    "Ma préférence d'engagement <em>(le comment ?)</em> : l'anneau extérieur",
    verbe_icons, descriptions_verbes, "verb"
)

st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 2px;'>🧩 ... sous la forme principale de :</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>La forme de mon engagement <em>(le quoi ?)</em> : l'emoticône du titre</span>", unsafe_allow_html=True)
formes = sorted(df["Forme"].unique())
# 1. Liste affichée : emoji + texte
formes_options = [f"{forme_emojis[f]} {f}" for f in formes]

# 2. Mapping inverse pour retrouver les vraies valeurs
formes_map = {f"{forme_emojis[f]} {f}": f for f in formes}

formes_selected_raw = st.sidebar.multiselect(
    "", options=formes_options, default=formes_options,
    label_visibility="collapsed"
)
formes_selected = [formes_map[f] for f in formes_selected_raw]


pref_piliers = afficher_sliders_personnalises(
    "🎯 Je souhaite développer ...",
    "Les 4 piliers JCI = les raisons de mon engagement <em>(le pourquoi ?)</em> : l'anneau intérieur",
    pilier_icons, descriptions_piliers, "pilier"
)

st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 2px;'>🌍 ... à un niveau :</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>La portée de mon engagement <em>(le où ?)</em> : au centre des anneaux </span>", unsafe_allow_html=True)
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n), label_visibility="collapsed")

# ---------- FILTRAGE DES DONNÉES ----------
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda nv: any(n in niveaux_selected for n in nv))]
df["Score"] = df.apply(lambda row: score(row, pref_engagements, pref_piliers), axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# ---------- AFFICHAGE TOP 9 ----------
top = df.head(9)

st.markdown("""
<div style='
    background-color: #F0F2F6;
    padding: 0.8rem 1rem;
    border-radius: 6px;
    margin-bottom: 0rem;
    text-align: center;
'>
<div style='font-size: 22px; line-height: 1; color: #333; margin-bottom: 0rem;'>
<b>Savoure ton TOP 9</b>
</div>
<div style='font-size: 15px; line-height: 1.6; color: #333; margin-bottom: 0rem;'>
Voici les opportunités qui correspondent à le mieux ta sélection actuelle. Qu'en penses-tu ? Partage ton assortiment de donuts avec d’autres Jaycees et ton parrain / marraine. 
</div>
""", unsafe_allow_html=True)

cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        emoji = forme_emojis.get(row["Forme"], "")
        st.markdown(f"<div style='font-size: 18px; font-weight: 600; text-align: center;'>{emoji} {row['Nom']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'>{formatter_description(row)}</div>", unsafe_allow_html=True)
        st.plotly_chart(make_visual(row, niveau_labels), use_container_width=True, key=f"top_{i}_{row['Nom']}")


# ---------- AUTRES OPPORTUNITÉS ----------
if len(df) > 9:
    st.markdown("""
    <div style='
    background-color: #F0F2F6;
    padding: 0.8rem 1rem;
    border-radius: 6px;
    margin-bottom: 0rem;
    text-align: center;
'>
<div style='font-size: 22px; line-height: 1; color: #333; margin-bottom: 0rem;'>
<b>🧁 Encore un peu de place ? Voici d’autres suggestions à ton goût</b>
</div>
<div style='font-size: 15px; line-height: 1.6; color: #333; margin-bottom: 0rem;'>
Pas tout à fait ce que tu cherchais, mais ces opportunités pourraient aussi t’inspirer
</div>

    """, unsafe_allow_html=True)

    others = df.iloc[9:21]
    cols = st.columns(4)
    for i, (_, row) in enumerate(others.iterrows()):
        with cols[i % 4]:
            emoji = forme_emojis.get(row["Forme"], "")
            st.markdown(f"<div style='font-size: 18px; font-weight: 600; text-align: center;'>{emoji} {row['Nom']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>{formatter_description(row)}</div>", unsafe_allow_html=True)
            st.plotly_chart(make_visual(row, niveau_labels, small=True), use_container_width=True, key=f"other_{i}_{row['Nom']}")
