
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

# Couleurs dynamiques pour les verbes (intensité)
couleurs_verbes_base = ["#FF9999", "#9999FF", "#99FF99", "#FFD580"]
couleurs_piliers = ["#b6d7a8", "#a4c2f4", "#f9cb9c", "#c9daf8"]

st.set_page_config(page_title="Rosace + Piliers", layout="wide")
st.title("🌼 Verbes en rosace 180° + piliers en barres descendantes")

# Fonction visuelle
def make_custom_visual(row):
    fig = go.Figure()

    # ROSACE HAUT (verbes)
    r_values = [row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]]
    theta = [45, 90, 135, 180]
    labels = ["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"]

    fig.add_trace(go.Barpolar(
        r=r_values,
        theta=theta,
        width=[30]*4,
        marker=dict(
            color=couleurs_verbes_base,
            line=dict(color="black", width=1)
        ),
        text=labels,
        hoverinfo="text+r",
        textposition="auto",
        opacity=0.9
    ))

    # BARRES BAS (piliers)
    piliers = ["Individu", "Entreprise", "Communauté", "International"]
    y_piliers = [-row["Individu"], -row["Entreprise"], -row["Communaute"], -row["Cooperation"]]

    fig.add_trace(go.Bar(
        x=piliers,
        y=y_piliers,
        marker_color=couleurs_piliers,
        text=piliers,
        textposition="outside",
        textfont=dict(color="black", size=12),
        name="Piliers",
    ))

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
                showline=False,
                tickfont=dict(size=12),
                ticks='',
                showticklabels=False
            ),
            radialaxis=dict(visible=False)
        ),
        barmode='overlay',
        height=520,
        margin=dict(t=20, b=40, l=20, r=20),
        showlegend=False,
        yaxis=dict(range=[-100, 10], visible=False),
        xaxis=dict(visible=True, showticklabels=False)
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
        st.plotly_chart(make_custom_visual(row), use_container_width=True)
