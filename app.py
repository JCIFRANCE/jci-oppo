import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# === Chargement et nettoyage des données ===
df = pd.read_csv("https://docs.google.com/spreadsheets/d/147E7GhixKkqECtBB1OKGqSy_CXt6skrucgHhPeU0Dog/export?format=csv", encoding="utf-8")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({
    "Autre": "Événement",
    "Evenement": "Événement",
    "Formation /atelier": "Formation",
    "Initiative /programme": "Programme",
    "Initiative/programme": "Programme"
})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", "Concours": "🏇 Concours", "Projet": "🚰 Projet",
    "Fonction": "💼 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
}
couleurs_verbes = {
    "Apprendre": "#0000FF",
    "Célébrer": "#FFD700",
    "Responsabiliser": "#FF0000",
    "Rencontrer": "#28A745"
}
couleurs_piliers = {
    "Développement individuel": "#A52A2A",
    "Entreprise": "#808080",
    "Communaute": "#FFA500",
    "Cooperation": "#800080"
}
verbes_labels = ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]
piliers_labels = ["Individu", "Entreprise", "Communauté", "International"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")

# === TITRE ET INTRODUCTION ===
st.markdown("<h1>🗌 Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)
st.markdown("""
Cette cartographie t’aide à découvrir les opportunités de la Jeune Chambre Économique qui correspondent à tes envies d'engagement. En bougeant les curseurs à gauche, tu fais ressortir celles qui te ressemblent. 

Tu y retrouves en un coup d'œil :
- Le ou les niveaux d'action au centre du visuel : Local / Régional / National / Zone / Mondial
- Les pictogrammes du type d'opportunité : 🎓 Formations et ateliers / 🎫 Événements / 🤝 En Équipe / 🧪 Programmes et initiatives / 🥇 Concours / 🛠️ Projets et actions
- **Ce que tu souhaites développer** : le cercle intérieur des piliers JCI <span style="color:#A52A2A">🟫 Développement personnel (pilier "Individu")</span> <span style="color:#808080">⬜ Compétences professionnelles et entrepreneuriales (pilier "Business")</span> <span style="color:#FFA500">🟧 Service au territoire (pilier "Communauté")</span> <span style="color:#800080">🟪 Coopération internationale (pilier "International")</span>  
- **Comment tu préfères t'impliquer** : le cercle extérieur : <span style="color:#0000FF">🟦 Apprendre</span> <span style="color:#FFD700">🟨 Célébrer</span> <span style="color:#FF0000">🟥 Prendre des responsabilités</span> <span style="color:#28A745">🟩 Se rencontrer</span>
""", unsafe_allow_html=True)

# === Interface de sélection utilisateur ===
with st.sidebar:
    st.markdown("## 🗺️ Découvre les opportunités JCE/JCI qui te correspondent")

    st.markdown("### 💓 Ce qui me fait vibrer c'est ...")
    pref_engagements = {}
    for key, color in couleurs_verbes.items():
        st.markdown(f"<span style='color:{color}'>{key}</span>", unsafe_allow_html=True)
        pref_engagements[key] = st.slider("", 0, 100, 25, key=f"verb_{key}", label_visibility="collapsed")

    st.markdown("### 🎯 Je souhaite développer ...")
    pref_piliers = {}
    for key, color in couleurs_piliers.items():
        st.markdown(f"<span style='color:{color}'>{key}</span>", unsafe_allow_html=True)
        pref_piliers[key] = st.slider("", 0, 100, 25, key=f"pilier_{key}", label_visibility="collapsed")

    st.markdown("### 🌍 ... à un niveau :")
    niveaux = ["L", "R", "N", "Z", "M"]
    niveaux_selected = st.multiselect("", niveaux, default=niveaux, format_func=lambda x: niveau_labels[x], label_visibility="collapsed")

    st.markdown("### 🧩 ... sous la forme principale de :")
    formes = sorted(df["Forme"].unique())
    formes_selected = st.multiselect("", formes, default=formes, format_func=lambda f: forme_emojis.get(f, f), label_visibility="collapsed")

# === Filtrage et scoring ===
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    s1 = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s2 = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s1 + s2) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# === Visualisation ===
def make_visual(row, i, small=False):
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=piliers_labels,
        marker=dict(colors=list(couleurs_piliers.values())),
        hole=0.3,
        textinfo='none',
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        showlegend=False
    ))

    values, labels, colors = [], [], []
    for j, k in enumerate(verbe_map.keys()):
        v = row.get(k, 0)
        if v > 0:
            values.append(v)
            labels.append(verbe_map[k])
            colors.append(couleurs_verbes[k])

    fig.add_trace(go.Pie(
        values=values, labels=labels,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='none',
        showlegend=False
    ))
    fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=260 if not small else 180)
    return fig

# === Affichage des résultats ===
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], row["Forme"])
        st.markdown(f"#### {picto} — {row['Nom']}")
        st.plotly_chart(make_visual(row, i), use_container_width=True)

if len(df) > 9:
    st.markdown("### 🔍 D'autres opportunités proches de tes critères")
    other = df.iloc[9:19]
    cols = st.columns(2)
    for i, (_, row) in enumerate(other.iterrows()):
        with cols[i % 2]:
            niveaux_txt = ", ".join(niveau_labels.get(n, n) for n in row["Niveau"])
            st.markdown(f"**{row['Nom']}** *({niveaux_txt})*")
            st.plotly_chart(make_visual(row, i + 1000, small=True), use_container_width=True)
