
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({
    "Autre": "Événement",
    "Evenement": "Événement",
    "Formation /atelier": "Formation",
    "Initiative /programme": "Programme",
    "Initiative/programme": "Programme"
})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Mappings
verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", 
    "Concours": "🥇 Concours", 
    "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", 
    "Equipe": "🤝 Équipe", 
    "Événement": "🎫 Événement", 
    "Formation": "🎓 Formation"
}

# Couleurs
couleurs_verbes = ["#0000FF", "#FFD700", "#FF0000", "#28A745"]
couleurs_piliers = ["#A52A2A", "#808080", "#FFA500", "#800080"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités")

# Visualisation
def make_visual(row, i):
    fig = go.Figure()

    # Centre : piliers
    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=["Individu", "Entreprise", "Communauté", "International"],
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        showlegend=False
    ))

    # Donut externe : verbes ≠ 0 uniquement
    donut_values = []
    donut_labels = []
    donut_colors = []
    for j, (col, label) in enumerate(verbe_map.items()):
        value = row.get(col, 0)
        if value > 0:
            donut_values.append(value)
            donut_labels.append(label)
            donut_colors.append(couleurs_verbes[j])

    fig.add_trace(go.Pie(
        values=donut_values,
        labels=donut_labels,
        marker=dict(colors=donut_colors, line=dict(color="white", width=2)),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='label',
        hovertemplate='<b style="font-size:16px;">%{label}</b><extra></extra>',
        showlegend=False
    ))

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    return fig

# Affichage en grille compacte
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        try:
            picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"<div style='height:360px'><h5>{picto} — {row['Nom']} <em style='font-size:90%'>{niveaux_txt}</em></h5>", unsafe_allow_html=True)
            st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{i}")
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception:
            st.error("❌ Erreur lors de l’affichage de cette opportunité.")
