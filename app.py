
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

# Pictogrammes + légende
forme_emojis = {
    "Programme": "🧠 [Programme]",
    "Concours": "🥇 [Concours]",
    "Projet": "🛠️ [Projet]",
    "Fonction": "👔 [Fonction]",
    "Equipe": "🤝 [Équipe]",
    "Autre": "🎯 [Autre]"
}

# Couleurs fun et transparentes
couleurs_piliers = ["rgba(255,99,132,0.6)", "rgba(54,162,235,0.6)", "rgba(255,206,86,0.6)", "rgba(75,192,192,0.6)"]

st.set_page_config(page_title="Explorer les opportunités JCI", layout="wide")
st.title("🎯 Explorer les opportunités JCI selon vos préférences")

# --- Sidebar : triple filtre ---
st.sidebar.header("🔎 Filtres")

# Formats
formes_disponibles = df["Forme"].dropna().unique().tolist()
formes_selectionnees = st.sidebar.multiselect("🧩 Formats", options=formes_disponibles, default=formes_disponibles)

# Piliers
st.sidebar.markdown("### 🌍 Piliers")
pref_piliers = {
    "Individu": st.sidebar.slider("Développement personnel", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Business", 0, 100, 25),
    "Communauté": st.sidebar.slider("Communauté", 0, 100, 25),
    "Coopération": st.sidebar.slider("International", 0, 100, 25),
}

# Engagements
st.sidebar.markdown("### 🧭 Engagements")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Prendre des responsabilités", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Se rencontrer", 0, 100, 25),
}

# --- Filtrage et score ---
df = df[df["Forme"].isin(formes_selectionnees)]

def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# --- Affichage 3 par ligne ---
st.subheader("🖼️ Opportunités sélectionnées (Top 9)")
cols = st.columns(3)
for i in range(min(9, len(df))):
    row = df.loc[i]
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], "📌 [Inconnu]")
        st.markdown(f"### {picto} {row['Nom']}")

        # Radar et camembert combinés
        fig = go.Figure()

        # Radar engagement
        fig.add_trace(go.Scatterpolar(
            r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"], row["Apprendre"]],
            theta=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer", "Apprendre"],
            fill='toself',
            name="Engagement",
            line_color="black",
            fillcolor="lightgray"
        ))

        # Camembert piliers plein (sous radar)
        valeurs_piliers = [row["Individu"], row["Entreprise"], row["Communauté"], row["Coopération"]]
        fig.add_trace(go.Pie(
            values=valeurs_piliers,
            labels=["Individu", "Entreprise", "Communauté", "Coopération"],
            marker=dict(colors=couleurs_piliers),
            hole=0.0,
            direction="clockwise",
            sort=False,
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

# --- Tableau final ---
st.subheader("📊 Autres opportunités classées par affinité")
hover_texts = df.apply(lambda r: f"{forme_emojis.get(r['Forme'], '')} {r['Nom']}", axis=1)
st.dataframe(df[["Nom", "Forme", "Score"]], use_container_width=True)
