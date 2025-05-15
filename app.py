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
couleurs_verbes = ["#0000FF", "#FFD700", "#FF0000", "#28A745"]
couleurs_piliers = ["#A52A2A", "#808080", "#FFA500", "#800080"]
verbes_labels = ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]
piliers_labels = ["Individu", "Entreprise", "Communauté", "International"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")

# === STYLE CSS PERSONNALISÉ ===
st.markdown("""
<style>
div.slider-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.5rem;
}
div.slider-item {
    width: 48%;
}
section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"] {
    display: none !important;
}
section[data-testid="stSidebar"] .stSlider {
    margin-top: -10px;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# === TITRE ET INTRODUCTION ===
st.markdown("<h1>🗌 Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)
st.markdown("""
Cette cartographie t’aide à découvrir les opportunités de la Jeune Chambre Économique qui correspondent à tes envies d'engagement. 

- **Ce que tu souhaites développer** : à l'intérieur du cercle
- **Comment tu préfères t'impliquer** : à l’extérieur du cercle
- **Type d’opportunité** : les pictogrammes
- **Niveaux d’action** : au centre
""", unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.markdown("## 🗌 Découvre les opportunités JCE/JCI qui te correspondent")

# SLIDERS VERBES
st.sidebar.markdown("### 💓 Ce qui me fait vibrer c'est ...")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Ma préférence d'engagement : le <em>comment</em></span>", unsafe_allow_html=True)

verbe_icons = {
    "Apprendre": ("🟦", "Apprendre", "#0000FF"),
    "Célébrer": ("🟨", "Célébrer", "#FFD700"),
    "Responsabiliser": ("🟥", "Prendre des responsabilités", "#FF0000"),
    "Rencontrer": ("🟩", "Se rencontrer", "#28A745")
}

st.sidebar.markdown("<div class='slider-grid'>", unsafe_allow_html=True)
pref_engagements = {}
for key, (emoji, label, color) in verbe_icons.items():
    st.sidebar.markdown(f"<div class='slider-item'>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<span style='color:{color}; font-weight:500;'>{emoji} {label}</span>", unsafe_allow_html=True)
    value = st.sidebar.slider("", 0, 100, 25, key=f"verb_{key}", label_visibility="collapsed")
    pref_engagements[key] = value
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# SLIDERS PILIERS
st.sidebar.markdown("### 🌟 Je souhaite développer ...")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Les 4 piliers JCI = le <em>pourquoi</em></span>", unsafe_allow_html=True)

pilier_icons = {
    "Développement individuel": ("🟫", "Individu", "#A52A2A"),
    "Entreprise": ("⬜", "Entreprise", "#808080"),
    "Communaute": ("🟧", "Communauté", "#FFA500"),
    "Cooperation": ("🟪", "International", "#800080")
}

st.sidebar.markdown("<div class='slider-grid'>", unsafe_allow_html=True)
pref_piliers = {}
for key, (emoji, label, color) in pilier_icons.items():
    st.sidebar.markdown(f"<div class='slider-item'>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<span style='color:{color}; font-weight:500;'>{emoji} {label}</span>", unsafe_allow_html=True)
    value = st.sidebar.slider("", 0, 100, 25, key=f"pilier_{key}", label_visibility="collapsed")
    pref_piliers[key] = value
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# AUTRES FILTRES
st.sidebar.markdown("### 🌍 ... à un niveau :")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Quelle portée a mon engagement : le <em>où</em></span>", unsafe_allow_html=True)
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
                                          format_func=lambda n: niveau_labels.get(n, n),
                                          label_visibility="collapsed")
formes = sorted(df["Forme"].unique().tolist())
st.sidebar.markdown("### 🧩 ... sous la forme de :")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>La forme de mon engagement : le <em>quoi</em></span>", unsafe_allow_html=True)
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: forme_emojis.get(f, f),
                                         label_visibility="collapsed")

# === FILTRAGE ET SCORE ===
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# === VISUALISATION OPPORTUNITES ===
def make_visual(row, i, small=False):
    niveaux_list = [niveau_labels.get(n, n) for n in row["Niveau"]]
    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=piliers_labels,
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False
    ))

    vals, labels, cols = [], [], []
    for j, (col, label) in enumerate(verbe_map.items()):
        val = row.get(col, 0)
        if val > 0:
            vals.append(val)
            labels.append(label)
            cols.append(couleurs_verbes[j])

    fig.add_trace(go.Pie(
        values=vals, labels=labels,
        marker=dict(colors=cols, line=dict(color="white", width=2)),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False
    ))

    if not small:
        for j, txt in enumerate(niveaux_list):
            fig.add_annotation(
                text=txt,
                showarrow=False,
                font=dict(size=11, color="black"),
                align="center",
                x=0.5, y=0.5 - j * 0.09,
                xanchor='center', yanchor='middle',
                borderpad=4
            )

    fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=260 if not small else 180)
    return fig

# Affichage des 9 premières opportunités
top = df.head(9)
st.markdown("### ")
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], row["Forme"])
        st.markdown(f"#### {picto} — {row['Nom']}")
        st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{i}")

# Opportunités suivantes
if len(df) > 9:
    st.markdown("### 🔍 D'autres opportunités proches de tes critères")
    other = df.iloc[9:19]
    cols = st.columns(2)
    for i, (_, row) in enumerate(other.iterrows()):
        with cols[i % 2]:
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"**{row['Nom']}** *({niveaux_txt})*")
            st.plotly_chart(make_visual(row, i+1000, small=True), use_container_width=True)
