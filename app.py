
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
niveau_labels = {"L": "🏘️ Local", "R": "🏙️ Régional", "N": "🇫🇷 National", "Z": "🌍 Zone", "M": "🌐 Monde"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

# Couleurs
couleurs_verbes = ["#FF4B4B", "#4B6CFF", "#28A745", "#FF9900"]
couleurs_piliers_degrade = ["#FFC0CB", "#B0E0E6", "#FFFACD", "#D8BFD8"]

st.set_page_config(page_title="Donut + Camembert central dégradé", layout="wide")
st.title("🍩 Donut pour les verbes + camembert central dégradé pour les piliers")

# Sélections
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect(
    "🧩 Formats", options=formes, default=formes,
    format_func=lambda f: forme_emojis.get(f, f"📌 {f}")
)
if not formes_selected:
    st.sidebar.warning("Sélectionnez au moins un format.")
    st.stop()

niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect(
    "🌍 Niveaux", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n)
)
if not niveaux_selected:
    st.sidebar.warning("Sélectionnez au moins un niveau.")
    st.stop()

st.sidebar.markdown("### 🧭 Engagements")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Responsabiliser", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Rencontrer", 0, 100, 25),
}

st.sidebar.markdown("### 🌐 Piliers")
pref_piliers = {
    "Individu": st.sidebar.slider("Individu", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Entreprise", 0, 100, 25),
    "Communaute": st.sidebar.slider("Communauté", 0, 100, 25),
    "Cooperation": st.sidebar.slider("International", 0, 100, 25),
}

# Filtrage et score
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Visualisation combinée
def make_donut_and_gradient(row):
    fig = go.Figure()

    # Camembert central (piliers)
    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=["Individu", "Entreprise", "Communauté", "International"],
        marker=dict(colors=couleurs_piliers_degrade),
        hole=0.3,
        domain={'x': [0.2, 0.8], 'y': [0.2, 0.8]},
        textinfo='none',
        sort=False,
        showlegend=False
    ))

    # Donut extérieur (verbes)
    fig.add_trace(go.Pie(
        values=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]],
        labels=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"],
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textposition='inside',
        textinfo='label+percent',
        sort=False,
        showlegend=False
    ))

    fig.update_layout(
        margin=dict(t=20, b=20, l=0, r=0),
        height=400
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
        st.plotly_chart(make_donut_and_gradient(row), use_container_width=True)
