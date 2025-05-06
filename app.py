
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données
df = pd.read_csv("data.csv")

# Normalisation
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Emojis
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

# Couleurs
couleurs_piliers = ["#b6d7a8", "#a4c2f4", "#f9cb9c", "#c9daf8"]
couleurs_verbes = ["#FF0000", "#0000FF", "#008000", "#FFA500"]

st.set_page_config(page_title="Donut + Marimekko JCI", layout="wide")
st.title("📊 Visualisation hybride : Verbes en donut, Piliers en Marimekko central")

def make_marimekko_donut(row, size=400):
    total = sum([row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]])
    widths = [row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]]
    widths = [w / total for w in widths]

    base_x = 0
    shapes = []
    for i, w in enumerate(widths):
        shapes.append(dict(
            type="rect",
            x0=base_x, x1=base_x + w,
            y0=0.4, y1=0.6,
            xref='paper', yref='paper',
            fillcolor=couleurs_piliers[i],
            line=dict(width=0)
        ))
        base_x += w

    fig = go.Figure()

    # Donut des verbes
    fig.add_trace(go.Pie(
        values=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]],
        labels=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"],
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textposition='inside',
        textinfo='label',
        showlegend=False,
        direction="clockwise",
        sort=False
    ))

    fig.update_layout(
        shapes=shapes,
        margin=dict(t=20, b=20, l=0, r=0),
        height=size
    )

    return fig

# Affichage
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
        st.plotly_chart(make_marimekko_donut(row), use_container_width=True)
