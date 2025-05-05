
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement et préparation des données
df = pd.read_excel("cartographie_des_opportunités_JCE.xlsx", sheet_name="Feuille 1", skiprows=2)
df = df.rename(columns={
    "Opportunité": "Nom",
    "Type": "Forme",
    "Pillier Individu": "Individu",
    "Pillier Entreprise": "Entreprise",
    "Pillier Communauté": "Communauté",
    "Pillier coopération internationale": "Coopération",
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Prendre des responsabilités": "Responsabiliser",
    "Se rencontrer": "Rencontrer"
})
df = df.dropna(subset=["Nom"])

# Conversion en numérique
for col in ["Individu", "Entreprise", "Communauté", "Coopération", "Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df.fillna(0, inplace=True)

# Liste des formes avec symboles associés
forme_symbols = {
    "Programme": "circle",
    "Concours": "star",
    "Projet": "triangle-up",
    "Fonction": "square",
    "Equipe": "diamond",
    "Autre": "cross"
}

# Interface Streamlit
st.set_page_config(page_title="Explorer les opportunités JCI", layout="wide")
st.title("🎯 Explorer les opportunités JCI selon vos envies")

# Choix de la forme (filtrage)
formes_disponibles = df["Forme"].unique().tolist()
forme_selectionnee = st.sidebar.selectbox("🔘 Filtrer par forme d’opportunité", options=["Toutes"] + formes_disponibles)

# Curseurs sur les verbes d’engagement
st.sidebar.header("🧭 Vos préférences d'engagement")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Prendre des responsabilités", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Se rencontrer", 0, 100, 25),
}

# Filtrage par forme
if forme_selectionnee != "Toutes":
    df = df[df["Forme"] == forme_selectionnee]

# Calcul du score d'affinité basé sur les verbes
def score(row):
    return sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score")

# Affichage des opportunités avec radar et camembert
st.subheader("📌 Opportunités triées par affinité avec vos préférences")

top = df.head(10)
cols = st.columns(2)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 2]:
        st.markdown(f"### {row['Nom']}")

        # Définir la forme pour cette opportunité
        symbole = forme_symbols.get(row["Forme"], "circle")

        # Radar pour les 4 verbes
        radar = go.Figure()

        radar.add_trace(go.Scatterpolar(
            r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"], row["Apprendre"]],
            theta=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer", "Apprendre"],
            fill='toself',
            name="Engagement",
            marker_symbol=symbole
        ))

        # Ajouter une couche "camembert" pour les piliers en arrière-plan
        valeurs_piliers = [row["Individu"], row["Entreprise"], row["Communauté"], row["Coopération"]]
        total = sum(valeurs_piliers)
        labels = ["Individu", "Entreprise", "Communauté", "Coopération"]

        radar.add_trace(go.Pie(
            values=valeurs_piliers,
            labels=labels,
            hole=0.6,
            direction='clockwise',
            textinfo='none',
            showlegend=False,
            domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]}
        ))

        radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=10, r=10, t=30, b=30),
            height=400
        )

        st.plotly_chart(radar, use_container_width=True)
