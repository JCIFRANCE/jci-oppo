
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger depuis Google Sheets ou fichier local
df = pd.read_csv("data.csv")

# Emoji par niveau
niveau_emoji = {
    "L": "🏘️ [Local]",
    "R": "🏙️ [Régional]",
    "N": "🇫🇷 [National]",
    "Z": "🌍 [Zone]",
    "M": "🌐 [Monde]"
}

forme_emojis = {
    "Programme": "🧠 [Programme]",
    "Concours": "🥇 [Concours]",
    "Projet": "🛠️ [Projet]",
    "Fonction": "👔 [Fonction]",
    "Equipe": "🤝 [Équipe]",
    "Autre": "🎯 [Autre]"
}

couleurs_piliers = ["rgba(255,99,132,0.6)", "rgba(54,162,235,0.6)", "rgba(255,206,86,0.6)", "rgba(75,192,192,0.6)"]

st.set_page_config(page_title="JCI Explorer", layout="wide")
st.title("🌟 Explorer les opportunités JCI selon vos préférences")

# Sidebar
st.sidebar.header("🔎 Filtres")
formes = df["Forme"].unique().tolist()
formes_selected = st.sidebar.multiselect("🧩 Formats", formes, default=formes)

niveaux = df["Niveau"].unique().tolist()
niveaux_selected = st.sidebar.multiselect("🌍 Niveaux", niveaux, default=niveaux)

st.sidebar.markdown("### 🧭 Engagements")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Prendre des responsabilités", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Se rencontrer", 0, 100, 25),
}

st.sidebar.markdown("### 🌍 Piliers")
pref_piliers = {
    "Individu": st.sidebar.slider("Individu", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Entreprise", 0, 100, 25),
    "Cooperation": st.sidebar.slider("International", 0, 100, 25),
    "Communaute": st.sidebar.slider("Communauté", 0, 100, 25),
}

# Filtrage
df = df[df["Forme"].isin(formes_selected) & df["Niveau"].isin(niveaux_selected)]

def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score")

# Affichage
st.subheader("🎯 Opportunités sélectionnées")
cols = st.columns(3)
for i in range(min(9, len(df))):
    row = df.iloc[i]
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], "📌 [Autre]")
        niveau = niveau_emoji.get(row["Niveau"], "")
        st.markdown(f"### {picto} {row['Nom']} {niveau}")

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"], row["Apprendre"]],
            theta=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer", "Apprendre"],
            fill='toself',
            name="Engagement",
            line_color="black",
            fillcolor="lightgray"
        ))

        fig.add_trace(go.Pie(
            values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
            labels=["Individu", "Entreprise", "Communauté", "International"],
            marker=dict(colors=couleurs_piliers),
            hole=0.0,
            textinfo="none",
            showlegend=False,
            domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]}
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=10, r=10, t=30, b=30),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Tableau final
st.subheader("📋 Tableau des opportunités")
st.dataframe(df[["Nom", "Forme", "Niveau", "Score"]], use_container_width=True)
