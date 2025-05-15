import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# === Chargement et nettoyage des données ===
df = pd.read_csv("https://docs.google.com/spreadsheets/d/147E7GhixKkqECtBB1OKGqSy_CXt6skrucgHhPeU0Dog/export?format=csv", encoding="utf-8")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({
    "Autre": "Événement",
    "Evenement": "Événement",
    "Formation /atelier": "Formation",
    "Initiative /programme": "Programme",
    "Initiative/programme": "Programme"
})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", "Concours": "🏇 Concours", "Projet": "🚰 Projet",
    "Fonction": "💼 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
}
couleurs_verbes = {
    "Apprendre": "#0000FF",
    "Célébrer": "#FFD700",
    "Responsabiliser": "#FF0000",
    "Rencontrer": "#28A745"
}
couleurs_piliers = {
    "Développement individuel": "#A52A2A",
    "Entreprise": "#808080",
    "Communaute": "#FFA500",
    "Cooperation": "#800080"
}
verbes_labels = ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]
piliers_labels = ["Individu", "Entreprise", "Communauté", "International"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")

# === TITRE ET INTRODUCTION ===
st.markdown("<h1>🗌 Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)
st.markdown("""
Cette cartographie t’aide à découvrir les opportunités de la Jeune Chambre Économique qui correspondent à tes envies d'engagement. En bougeant les curseurs à gauche, tu fais ressortir celles qui te ressemblent. 

Tu y retrouves en un coup d'œil :
- Le ou les niveaux d'action au centre du visuel : Local / Régional / National / Zone / Mondial
- Les pictogrammes du type d'opportunité : 🎓 Formations et ateliers / 🎫 Événements / 🤝 En Équipe / 🧪 Programmes et initiatives / 🥇 Concours / 🛠️ Projets et actions
- **Ce que tu souhaites développer** : le cercle intérieur des piliers JCI <span style=\"color:#A52A2A\">🟫 Développement personnel (pilier \"Individu\")</span> <span style=\"color:#808080\">⬜ Compétences professionnelles et entrepreneuriales (pilier \"Business\")</span> <span style=\"color:#FFA500\">🟧 Service au territoire (pilier \"Communauté\")</span> <span style=\"color:#800080\">🟪 Coopération internationale (pilier \"International\")</span>  
- **Comment tu préfères t'impliquer** : le cercle extérieur : <span style=\"color:#0000FF\">🟦 Apprendre</span> <span style=\"color:#FFD700\">🟨 Célébrer</span> <span style=\"color:#FF0000\">🟥 Prendre des responsabilités</span> <span style=\"color:#28A745\">🟩 Se rencontrer</span>
""", unsafe_allow_html=True)

# === CSS dynamique par slider ===
slider_styles = """<style>
%s
</style>""" % "\n".join([
    f"input[key=\"verb_{key}\"]::-webkit-slider-thumb {{ background: {color} !important; }}\n"
    f"input[key=\"verb_{key}\"]::-moz-range-thumb {{ background: {color} !important; }}"
    for key, color in couleurs_verbes.items()
] + [
    f"input[key=\"pilier_{key}\"]::-webkit-slider-thumb {{ background: {color} !important; }}\n"
    f"input[key=\"pilier_{key}\"]::-moz-range-thumb {{ background: {color} !important; }}"
    for key, color in couleurs_piliers.items()
])

st.markdown(slider_styles, unsafe_allow_html=True)

# === INTERFACE SIDEBAR ===
with st.sidebar:
    st.markdown("## 🗺️ Découvre les opportunités JCE/JCI qui te correspondent")
    st.markdown("### 💓 Ce qui me fait vibrer c'est ...")
    st.markdown("<span style='font-size: 11px; color: grey;'>Ma préférence d'engagement : le <em>comment</em></span>", unsafe_allow_html=True)

    verbe_icons = {
        "Apprendre": ("🟦", "Apprendre"),
        "Célébrer": ("🟨", "Célébrer"),
        "Responsabiliser": ("🟥", "Prendre des responsabilités"),
        "Rencontrer": ("🟩", "Se rencontrer")
    }

    pref_engagements = {}
    cols = st.columns(2)
    for idx, (key, (emoji, label)) in enumerate(verbe_icons.items()):
        with cols[idx % 2]:
            st.markdown(f"<span style='color:{couleurs_verbes[key]}; font-weight:500;'>{emoji} {label}</span>", unsafe_allow_html=True)
            value = st.slider("", 0, 100, 25, key=f"verb_{key}", label_visibility="collapsed")
            pref_engagements[key] = value

    st.markdown("### 🎯 Je souhaite développer ...")
    st.markdown("<span style='font-size: 11px; color: grey;'>Les 4 piliers JCI = les raisons de mon engagement : le <em>pourquoi</em></span>", unsafe_allow_html=True)

    pilier_icons = {
        "Développement individuel": ("🟫", "Individu"),
        "Entreprise": ("⬜", "Entreprise"),
        "Communaute": ("🟧", "Communauté"),
        "Cooperation": ("🟪", "International")
    }

    pref_piliers = {}
    cols = st.columns(2)
    for idx, (key, (emoji, label)) in enumerate(pilier_icons.items()):
        with cols[idx % 2]:
            st.markdown(f"<span style='color:{couleurs_piliers[key]}; font-weight:500;'>{emoji} {label}</span>", unsafe_allow_html=True)
            value = st.slider("", 0, 100, 25, key=f"pilier_{key}", label_visibility="collapsed")
            pref_piliers[key] = value

    st.markdown("### 🌍 ... à un niveau :")
    st.markdown("<span style='font-size: 11px; color: grey;'>Quelle portée a mon engagement : le <em>où</em></span>", unsafe_allow_html=True)
    niveaux = ["L", "R", "N", "Z", "M"]
    niveaux_selected = st.multiselect("", options=niveaux, default=niveaux,
                                      format_func=lambda n: niveau_labels.get(n, n),
                                      label_visibility="collapsed")

    st.markdown("### 🧩 ... sous la forme principale de :")
    st.markdown("<span style='font-size: 11px; color: grey;'>La forme de mon engagement : le <em>quoi</em></span>", unsafe_allow_html=True)
    formes = sorted(df["Forme"].unique().tolist())
    formes_selected = st.multiselect("", options=formes, default=formes,
                                     format_func=lambda f: forme_emojis.get(f, f),
                                     label_visibility="collapsed")
