
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données
df = pd.read_csv("data.csv")

# Nettoyage
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Emoji et couleurs
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
forme_emojis = {
    "Programme": "🧠 Programme",
    "Concours": "🥇 Concours",
    "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction",
    "Equipe": "🤝 Équipe",
    "Événement": "🎫 Événement"
}
couleurs_piliers = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"]
couleurs_verbes = ["#9966FF", "#FF9F40", "#C9CBCF", "#00A676"]

# Interface
st.set_page_config(page_title="Double Donut JCI", layout="wide")
st.title("🧁 Visualisation des opportunités : piliers & verbes imbriqués")

top = df.head(9)
cols = st.columns(3)

for i in range(min(9, len(top))):
    row = top.iloc[i]
    with cols[i % 3]:
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        forme_picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        st.markdown(f"### {forme_picto} — {row['Nom']} {niveaux_str}")

        fig = go.Figure()

        # Donut intérieur : piliers
        fig.add_trace(go.Pie(
            values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
            labels=["Individu", "Entreprise", "Communauté", "International"],
            marker=dict(colors=couleurs_piliers),
            hole=0.3,
            domain={'x': [0, 1], 'y': [0, 1]},
            name="Piliers",
            textposition='inside',
            textinfo='label+percent',
            sort=False,
            direction='clockwise',
            showlegend=False
        ))

        # Donut extérieur : verbes
        fig.add_trace(go.Pie(
            values=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]],
            labels=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"],
            marker=dict(colors=couleurs_verbes),
            hole=0.6,
            domain={'x': [0, 1], 'y': [0, 1]},
            name="Engagements",
            textposition='inside',
            textinfo='label+percent',
            sort=False,
            direction='clockwise',
            showlegend=False
        ))

        fig.update_layout(
            margin=dict(t=20, b=20, l=0, r=0),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
        
