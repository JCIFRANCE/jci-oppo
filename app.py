
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
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

st.set_page_config(page_title="Verbes en rosace + piliers en barres", layout="wide")
st.title("🌸 Rosace 180° pour verbes + piliers en barres descendantes")

# Fonction de visualisation
def make_rosace_and_legs(row):
    fig = go.Figure()

    # Rosace 180° en haut
    fig.add_trace(go.Barpolar(
        r=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]],
        theta=[45, 90, 135, 180],
        width=[30, 30, 30, 30],
        marker_color=couleurs_verbes,
        marker_line_color="black",
        marker_line_width=1,
        opacity=0.8,
        name="Engagements"
    ))

    # Barres piliers en bas (comme jambes)
    x_piliers = ["Individu", "Entreprise", "Communauté", "International"]
    y_piliers = [-row["Individu"], -row["Entreprise"], -row["Communaute"], -row["Cooperation"]]

    fig.add_trace(go.Bar(
        x=x_piliers,
        y=y_piliers,
        marker_color=couleurs_piliers,
        name="Piliers",
        width=0.5,
        offsetgroup=1
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], visible=True, angle=90),
            angularaxis=dict(direction="clockwise", rotation=90)
        ),
        barmode='overlay',
        height=500,
        margin=dict(t=40, b=40, l=40, r=40),
        showlegend=False,
        yaxis=dict(range=[-100, 0], visible=False),
        xaxis=dict(showticklabels=False)
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
        st.plotly_chart(make_rosace_and_legs(row), use_container_width=True)

