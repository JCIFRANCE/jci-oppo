

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

# Explication et légende
st.markdown("""
> Cette cartographie vous permet de **découvrir les multiples opportunités proposées par la Jeune Chambre Économique**, en fonction de ce que vous cherchez à vivre, développer ou expérimenter.
> 
> Pour chaque opportunité, un **donut vif** vous présente l’intensité des **4 verbes d’engagement** (Apprendre, Célébrer, Prendre des responsabilités, Se rencontrer), et un **centre en couleurs douces** représente la répartition des **4 piliers de développement** (Individu, Entreprise, Communauté, International).
""")

st.markdown("""
<div style="position: sticky; top: 0; background-color: white; z-index: 999; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
<h4>📍 Légende</h4>
<ul>
    <li><strong>Verbes (donut)</strong> :
        <span style="color:#0000FF">🟦 Apprendre</span>,
        <span style="color:#FFD700">🟨 Célébrer</span>,
        <span style="color:#FF0000">🟥 Prendre des responsabilités</span>,
        <span style="color:#28A745">🟩 Se rencontrer</span>.
    </li>
    <li><strong>Piliers (centre)</strong> :
        <span style="color:#A52A2A">🟫 Individu</span>,
        <span style="color:#808080">⬜ Entreprise</span>,
        <span style="color:#FFA500">🟧 Communauté</span>,
        <span style="color:#800080">🟪 International</span>.
    </li>
</ul>
<p>🔎 Utilisez les filtres à gauche pour personnaliser les opportunités affichées selon vos envies.</p>
</div>
""", unsafe_allow_html=True)

# Volet latéral
st.sidebar.markdown("### 🎯 Je recherche les opportunités Jeune Chambre qui me permettront de ...")
pref_engagements = {}
for col, label in verbe_map.items():
    pref_engagements[col] = st.sidebar.slider(label, 0, 100, 25, key=f"verb_{col}")

st.sidebar.markdown("### 🧩 Sous la forme de :")
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect(
    "Formats", options=formes, default=formes,
    format_func=lambda f: forme_emojis.get(f, f)
)

st.sidebar.markdown("### 🌍 À un niveau :")
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect(
    "Niveaux", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n)
)

st.sidebar.markdown("### 🌐 ... avec un impact sur :")
pref_piliers = {}
for pilier in ["Individu", "Entreprise", "Communaute", "Cooperation"]:
    pref_piliers[pilier] = st.sidebar.slider(pilier, 0, 100, 25, key=f"pilier_{pilier}")

# Filtrage
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

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

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=420)
    return fig

# Affichage
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        try:
            picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"#### {picto} — {row['Nom']} *{niveaux_txt}*")
            st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{i}")
        except Exception:
            st.error("❌ Erreur lors de l’affichage de cette opportunité.")
