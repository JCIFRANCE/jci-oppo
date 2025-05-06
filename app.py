
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données
df = pd.read_csv("data.csv")

# Corriger les valeurs de forme
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})

# Emoji par niveau
niveau_emoji = {
    "L": "🏘️",
    "R": "🏙️",
    "N": "🇫🇷",
    "Z": "🌍",
    "M": "🌐"
}

# Pictos par forme
forme_emojis = {
    "Programme": "🧠 Programme",
    "Concours": "🥇 Concours",
    "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction",
    "Equipe": "🤝 Équipe",
    "Événement": "🎫 Événement"
}

couleurs_piliers = ["rgba(255,99,132,0.6)", "rgba(54,162,235,0.6)",
                    "rgba(255,206,86,0.6)", "rgba(75,192,192,0.6)"]

st.set_page_config(page_title="JCI Explorer", layout="wide")
st.title("🌟 Explorer les opportunités JCI selon vos préférences")

# Convertir les niveaux multiples en listes
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in niveau_emoji])

# --- Sidebar avec pictos ---
st.sidebar.header("🔎 Filtres")

formes = df["Forme"].unique().tolist()
formes_labels = [forme_emojis[f] for f in formes]
formes_selected = st.sidebar.multiselect("🧩 Formats", options=formes, default=formes, format_func=lambda f: forme_emojis[f])

niveaux = ["L", "R", "N", "Z", "M"]
niveaux_labels = [niveau_emoji[n] for n in niveaux]
niveaux_selected = st.sidebar.multiselect("🌍 Niveaux", options=niveaux, default=niveaux, format_func=lambda n: niveau_emoji[n])

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
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda levels: any(n in niveaux_selected for n in levels))]

def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Affichage radar + camembert
st.subheader("🎯 Opportunités sélectionnées")
cols = st.columns(3)
for i in range(min(9, len(df))):
    row = df.loc[i]
    with cols[i % 3]:
        niveaux_str = " ".join([niveau_emoji[n] for n in row["Niveau"] if n in niveau_emoji])
        picto = forme_emojis.get(row["Forme"], "📌 Autre")
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")

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
            domain={'x': [0.1, 0.9], 'y': [0.1, 0.9]}
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                angularaxis=dict(
                    tickfont=dict(size=12, color="black")
                )
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=380
        )

        st.plotly_chart(fig, use_container_width=True)

# Tableau final
st.subheader("📋 Tableau des opportunités")
st.dataframe(df[["Nom", "Forme", "Score"]], use_container_width=True)
