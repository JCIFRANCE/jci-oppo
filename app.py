
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
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

# Dictionnaires
verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
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

# Page config
st.set_page_config(page_title="Cartographie des opportunités", layout="wide", initial_sidebar_state="expanded")

# Style CSS
st.markdown("""
<style>
section[data-testid="stSidebar"] .stSlider { margin-top: -6px; margin-bottom: 1px; }
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"],
section[data-testid="stSidebar"] .stSlider div[role="tooltip"],
section[data-testid="stSidebar"] .stSlider span {
    display: none !important;
}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h4 {
    margin-bottom: 0rem !important;
    margin-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown("<h1>🗺️ Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)

# Sidebar verbes
st.sidebar.markdown("## 💓 Ce qui me fait vibrer c'est ...")
descriptions_verbes = {
    "Apprendre": "se former, monter en compétence et grandir",
    "Célébrer": "fêter les réussites, marquer les jalons, garder du temps pour le plaisir",
    "Responsabiliser": "prendre le lead, transmettre, coacher",
    "Rencontrer": "se faire des amis, réseauter, se réunir autour d'une table"
}
verbe_icons = {
    "Apprendre": ("🟦", "Apprendre", "#0000FF"),
    "Célébrer": ("🟨", "Célébrer", "#FFD700"),
    "Responsabiliser": ("🟥", "Prendre des responsabilités", "#FF0000"),
    "Rencontrer": ("🟩", "Se rencontrer", "#28A745")
}
pref_engagements = {}
for k, (emoji, label, color) in verbe_icons.items():
    st.sidebar.markdown(f"""
    <div style='margin-bottom: 0.4rem;'>
        <span style='font-weight: 500;'>{emoji} {label}</span>
        <span style='font-weight: 300; font-size: 13px; color: grey;'> : {descriptions_verbes[k]}</span>
    </div>
    """, unsafe_allow_html=True)
    slider_id = f"verb_{k}"
    value = st.sidebar.slider("", 0, 100, 25, key=slider_id, label_visibility="collapsed")
    pref_engagements[k] = value

# Sidebar piliers
descriptions_piliers = {
    "Développement individuel": "Dév. personnel, valeurs, éthique",
    "Entreprise": "Compétences pro, entrepreneuriat",
    "Communaute": "Impact local, utilité publique",
    "Cooperation": "Ouverture, diplomatie internationale"
}
pilier_icons = {
    "Développement individuel": ("🟫", "Individu", "#A52A2A"),
    "Entreprise": ("⬜", "Entreprise", "#808080"),
    "Communaute": ("🟧", "Communauté", "#FFA500"),
    "Cooperation": ("🟪", "International", "#800080")
}
pref_piliers = {}
for p, (emoji, label, color) in pilier_icons.items():
    st.sidebar.markdown(f"""
    <div style='margin-bottom: 0.4rem;'>
        <span style='font-weight: 500;'>{emoji} {label}</span>
        <span style='font-weight: 300; font-size: 13px; color: grey;'> : {descriptions_piliers[p]}</span>
    </div>
    """, unsafe_allow_html=True)
    slider_id = f"pilier_{p}"
    value = st.sidebar.slider("", 0, 100, 25, key=slider_id, label_visibility="collapsed")
    pref_piliers[p] = value

# Sélections complémentaires
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect("Forme", options=formes, default=formes)
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("Niveau", options=niveaux, default=niveaux, format_func=lambda n: niveau_labels[n])

# Filtrage données
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

# Score
def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Visualisation
def make_visual(row, i, small=False):
    niveaux_list = [niveau_labels.get(n, n) for n in row["Niveau"]]
    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=piliers_labels,
        marker=dict(color=[
            couleurs_piliers["Développement individuel"],
            couleurs_piliers["Entreprise"],
            couleurs_piliers["Communaute"],
            couleurs_piliers["Cooperation"]
        ]),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False
    ))

    vals, labels, cols = [], [], []
    for verbe, label in verbe_map.items():
        val = row.get(verbe, 0)
        if val > 0:
            vals.append(val)
            labels.append(label)
            cols.append(couleurs_verbes[verbe])

    fig.add_trace(go.Pie(
        values=vals, labels=labels,
        marker=dict(color=cols, line=dict(color="white", width=2)),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False
    ))

    for j, txt in enumerate(niveaux_list):
        fig.add_annotation(
            text=txt,
            showarrow=False,
            font=dict(size=11, color="black"),
            align="center",
            x=0.5, y=0.5 - j * 0.09,
            xanchor='center', yanchor='middle'
        )

    fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=260 if not small else 180)
    return fig

# Affichage
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
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"**{row['Nom']}** *({niveaux_txt})*")
            st.plotly_chart(make_visual(row, i+1000, small=True), use_container_width=True)
