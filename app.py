
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
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

# Nettoyage des données numériques
for col in ["Individu", "Entreprise", "Communauté", "Coopération", "Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna()

st.title("🎯 Explorer les opportunités JCI selon vos envies")

# Sliders utilisateur : curseurs de préférences
st.sidebar.header("🧭 Vos préférences")
pref_piliers = {
    "Individu": st.sidebar.slider("Développement personnel", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Business", 0, 100, 25),
    "Communauté": st.sidebar.slider("Communauté", 0, 100, 25),
    "Coopération": st.sidebar.slider("International", 0, 100, 25),
}

pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Prendre des responsabilités", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Se rencontrer", 0, 100, 25),
}

def score_opportunité(row):
    score_piliers = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    score_engagements = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    return (score_piliers + score_engagements) ** 0.5

df["Score"] = df.apply(score_opportunité, axis=1)
df = df.sort_values("Score")

top = df.head(5)

st.subheader("🔎 Opportunités qui vous correspondent le mieux")
for _, row in top.iterrows():
    st.markdown(f"### {row['Nom']}")
    st.write(f"**Forme :** {row['Forme']}")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[row["Individu"], row["Entreprise"], row["Communauté"], row["Coopération"], row["Individu"]],
        theta=["Individu", "Entreprise", "Communauté", "Coopération", "Individu"],
        fill='toself',
        name="Piliers"
    ))
    fig.add_trace(go.Scatterpolar(
        r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"], row["Apprendre"]],
        theta=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer", "Apprendre"],
        fill='toself',
        name="Engagements"
    ))
    st.plotly_chart(fig, use_container_width=True)
