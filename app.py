
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Emojis
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}
couleurs_verbes = ["#FF9999", "#9999FF", "#66CC66", "#FFCC66"]
couleurs_piliers = ["#c9e4c5", "#bfd3f2", "#fcebbd", "#e6d0de"]

st.set_page_config(page_title="Rosace claire + barres nettes", layout="wide")
st.title("🌼 Verbes en rosace colorée + piliers en barres sous la ligne")

def make_clean_rosace_and_legs(row):
    # Rosace manuelle : chaque secteur = cercle rempli proportionnellement
    verbes = [("Apprendre", 0), ("Célébrer", 45), ("Responsabiliser", 90), ("Rencontrer", 135)]
    fig = go.Figure()

    # Rosace manuelle
    for i, (verbe, angle) in enumerate(verbes):
        level = row[verbe]
        color = couleurs_verbes[i]
        fig.add_trace(go.Barpolar(
            r=[level],
            theta=[angle],
            width=[40],
            marker=dict(color=color, opacity=min(0.4 + level / 120, 1)),
            hoverinfo="text",
            text=f"{verbe}: {level}",
            name=verbe,
        ))

    # Piliers en barres
    piliers = ["Individu", "Entreprise", "Communaute", "Cooperation"]
    x_vals = ["Individu", "Entreprise", "Communauté", "International"]
    y_vals = [-row["Individu"], -row["Entreprise"], -row["Communaute"], -row["Cooperation"]]

    fig.add_trace(go.Bar(
        x=x_vals,
        y=y_vals,
        marker_color=couleurs_piliers,
        name="Piliers",
        text=[f"{abs(val)}" for val in y_vals],
        textposition="outside",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(showline=False, showticklabels=False)
        ),
        xaxis=dict(title="", showline=False, zeroline=False),
        yaxis=dict(range=[-100, 120], visible=False),
        barmode='overlay',
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=500
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
        st.plotly_chart(make_clean_rosace_and_legs(row), use_container_width=True)
