
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

for col in ["Individu", "Entreprise", "Communauté", "Coopération", "Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df.fillna(0, inplace=True)

# Légende des formes avec pictos différents de ceux des textes JCI
forme_emojis = {
    "Programme": "🧩 [Programme]",
    "Concours": "🏆 [Concours]",
    "Projet": "📐 [Projet]",
    "Fonction": "🧑‍💼 [Fonction]",
    "Equipe": "🤝 [Équipe]",
    "Autre": "🎯 [Autre]"
}

# Couleurs vives et transparentes pour les piliers
couleurs_piliers = ["rgba(255,140,66,0.5)", "rgba(255,60,56,0.5)", "rgba(162,62,72,0.5)", "rgba(46,134,171,0.5)"]

st.set_page_config(page_title="Explorer les opportunités JCI", layout="wide")
st.title("🎯 Explorer les opportunités JCI selon vos envies")

# --- SIDEBAR ---
st.sidebar.header("🔘 Filtrer les opportunités")

# Forme (checkbox multiples)
formes_dispo = df["Forme"].dropna().unique().tolist()
formes_selectionnees = st.sidebar.multiselect("Formats :", options=formes_dispo, default=formes_dispo)

# Curseurs piliers
st.sidebar.subheader("🌐 Vos priorités par pilier")
pref_piliers = {
    "Individu": st.sidebar.slider("Développement personnel", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Business", 0, 100, 25),
    "Communauté": st.sidebar.slider("Communauté", 0, 100, 25),
    "Coopération": st.sidebar.slider("International", 0, 100, 25),
}

# Curseurs engagement
st.sidebar.subheader("🧭 Vos préférences d'engagement")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Prendre des responsabilités", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Se rencontrer", 0, 100, 25),
}

# --- FILTRAGE ---
df = df[df["Forme"].isin(formes_selectionnees)]

def score(row):
    score_engagements = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_piliers = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_engagements + score_piliers) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score")

# --- AFFICHAGE DES OPPORTUNITÉS ---
st.subheader("📌 Opportunités correspondant à vos critères")
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], "📌 [Inconnu]")
        st.markdown(f"### {picto} {row['Nom']}")

        radar = go.Figure()

        radar.add_trace(go.Scatterpolar(
            r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"], row["Apprendre"]],
            theta=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer", "Apprendre"],
            fill='toself',
            name="Engagement",
            line_color="black",
            fillcolor="lightgray"
        ))

        valeurs_piliers = [row["Individu"], row["Entreprise"], row["Communauté"], row["Coopération"]]
        labels = ["Individu", "Entreprise", "Communauté", "Coopération"]

        radar.add_trace(go.Pie(
            values=valeurs_piliers,
            labels=labels,
            hole=0.0,
            direction='clockwise',
            marker=dict(colors=couleurs_piliers),
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

# --- TABLEAU INTERACTIF ---
st.subheader("📄 Explorer d'autres opportunités")
import plotly.express as px

table_data = df[["Nom", "Forme", "Score"]].reset_index(drop=True)
fig_table = px.scatter(
    table_data,
    x="Nom",
    y="Score",
    hover_data=["Forme"],
    title="Classement par affinité",
    height=400
)
st.plotly_chart(fig_table, use_container_width=True)
