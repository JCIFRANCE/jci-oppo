
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Données
df = pd.read_csv("data.csv")

# Nettoyage
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
couleurs_piliers = ["#b6d7a8", "#a4c2f4", "#f9cb9c", "#c9daf8"]  # pastel
couleurs_verbes = ["#FF0000", "#0000FF", "#008000", "#FFA500"]   # vives

st.set_page_config(page_title="Double Donut Explorer", layout="wide")
st.title("🍩 Visualisation des opportunités JCI : piliers & verbes")

# Sélection formats et niveaux
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect(
    "🧩 Formats", options=formes, default=formes,
    format_func=lambda f: forme_emojis.get(f, f"📌 {f}")
)

niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect(
    "🌍 Niveaux", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n)
)

# Curseurs engagement
st.sidebar.markdown("### 🧭 Engagements")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Responsabiliser", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Rencontrer", 0, 100, 25),
}

# Curseurs piliers
st.sidebar.markdown("### 🌐 Piliers")
pref_piliers = {
    "Individu": st.sidebar.slider("Individu", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Entreprise", 0, 100, 25),
    "Communaute": st.sidebar.slider("Communauté", 0, 100, 25),
    "Cooperation": st.sidebar.slider("International", 0, 100, 25),
}

# Filtrage
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

# Score de proximité
def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Fonction donut
def make_double_donut(row, size=400, show_label=True):
    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=["Individu", "Entreprise", "Communauté", "International"],
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]},
        textposition='inside',
        textinfo='label' if show_label else 'none',
        showlegend=False,
        direction="clockwise",
        sort=False
    ))

    fig.add_trace(go.Pie(
        values=[row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]],
        labels=["Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"],
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textposition='inside',
        textinfo='label' if show_label else 'none',
        showlegend=False,
        direction="clockwise",
        sort=False
    ))

    fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=size)
    return fig

# Affichage principal
st.subheader("🎯 Opportunités sélectionnées")
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
        st.plotly_chart(make_double_donut(row), use_container_width=True)

# Opportunités complémentaires
others = df.iloc[9:19]
if not others.empty:
    st.subheader("🧩 Autres opportunités proches de vos critères")
    for _, row in others.iterrows():
        cols = st.columns([1, 4])
        with cols[0]:
            st.plotly_chart(make_double_donut(row, size=180, show_label=False), use_container_width=True)
        with cols[1]:
            st.markdown(f"**{forme_emojis.get(row['Forme'], row['Forme'])} — {row['Nom']}**<br>"
                        f"<span style='font-size: 14px'>{' '.join(niveau_emoji.get(n, '') for n in row['Niveau'])}</span>",
                        unsafe_allow_html=True)
