import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Chargement des données
df = pd.read_csv("https://docs.google.com/spreadsheets/d/147E7GhixKkqECtBB1OKGqSy_CXt6skrucgHhPeU0Dog/export?format=csv", encoding="utf-8")
df.columns = df.columns.str.strip()
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
    "Programme": "🧪 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
}

# Exemple de données
piliers_labels = ["Individu", "Entreprise", "Communauté", "International"]
couleurs_piliers = ["#765358", "#D3D3D3", "#E17D4F", "#8667D6"] 

verbes_labels = ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]
couleurs_verbes = ["#5E81D0", "#EEBD63", "#B74659", "#79C28F"]  

# Dictionnaires pour associer les labels aux couleurs
couleur_pilier_dict = dict(zip(piliers_labels, couleurs_piliers))
couleur_verbe_dict = dict(zip(verbes_labels, couleurs_verbes))


# Configuration de la page
st.set_page_config(
    page_title="Cartographie des opportunités",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé pour la sidebar
hide_elements = """
        <style>
            div[data-testid="stSliderTickBarMin"],
            div[data-testid="stSliderTickBarMax"] {
                display: none;
            }
        </style>
"""

st.markdown(hide_elements, unsafe_allow_html=True)

st.markdown("""
<style>
/* Réduction des marges autour des sliders */
section[data-testid="stSidebar"] .stSlider {
    margin-top: -6px;
    margin-bottom: 1px;
}

/* Cache tout texte dans les sliders */
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"],
section[data-testid="stSidebar"] .stSlider div[role="tooltip"],
section[data-testid="stSidebar"] .stSlider span {
    display: none !important;
}

/* Réduction des marges après les titres */
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h4 {
    margin-bottom: 0rem !important;
    margin-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Les opportunités de la Jeune Chambre ... en Donuts 🍩</h1>", unsafe_allow_html=True)
st.markdown("""
<h2>Identifie facilement les opportunités de la Jeune Chambre qui te correspondent !</h2>

**ETAPE 1. Personnalise tes préférences**
Utilise les curseurs et étquettes à gauche pour faire ressortir les opportunités qui te ressemblent le plus.

**ETAPE 2. Lis la cartographie en un coup d’œil**
Le cercle extérieur indique comment tu préfères t’impliquer. Le Cercle intérieur montre ce que tu souhaites développer à travers ton engagement. Les icônes dans le titre représentent la forme que prend l’opportunité (ex. formation, événement, projet…).
Le centre précise la portée de l’opportunité.

**Explore, ajuste, découvre ce qui te motive, et profite du plaisir de l'engagement !**
""", unsafe_allow_html=True)

# Filtrage utilisateur
st.sidebar.markdown("## 🗺️ Découvre les opportunités JCE/JCI qui correspondent à ton style d'engagement")

st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 0px;'>💓 Ce qui me fait vibrer c'est ...</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>Ma préférence d'engagement <em>(le comment ?)</em></span>", unsafe_allow_html=True)
# VERBES : carré + label + description légère
descriptions_verbes = {
    "Apprendre": "se former, monter en compétence et grandir",
    "Célébrer": "fêter les réussites, marquer les jalons, garder du temps pour le plaisir",
    "Responsabiliser": "prendre le lead, transmettre, coacher",
    "Rencontrer": "se faire des amis, réseauter, se réunir autour d'une table"
}

# Couleurs mises à jour pour correspondre aux emojis
verbe_icons = {
    "Apprendre": ("🟦", "Apprendre", "#5E81D0"),
    "Célébrer": ("🟨", "Célébrer", "#EEBD63"),
    "Responsabiliser": ("🟥", "Prendre des responsabilités", "#B74659"),
    "Rencontrer": ("🟩", "Se rencontrer", "#79C28F")
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
    value = st.sidebar.slider(
        label="",
        min_value=0,
        max_value=100,
        value=25,
        label_visibility="collapsed",
        key=slider_id
    )
    pref_engagements[k] = value
   
st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 2px;'>🧩 ... sous la forme principale de :</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>La forme de mon engagement <em>(le quoi ?)</em></span>", unsafe_allow_html=True)
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: forme_emojis.get(f, f),
                                         label_visibility="collapsed")

st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 2px;'>🎯 Je souhaite développer ...</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>Les 4 piliers JCI = les raisons de mon engagement <em>(le pourquoi ?)</em></span>", unsafe_allow_html=True)


# PILIERS : carré + label + description légère
descriptions_piliers = {
    "Développement individuel": "Savoir-être, développement personnel, outils du citoyen responsable, défense des valeurs, éthique",
    "Entreprise": "Savoir-faire, compétences de management, réseau business, tester ses idées",
    "Communaute": "Au serice du territoire et de l’intérêt général, benchmark des actions, agir pour construire un monde meilleur",
    "Cooperation": "dépasser les horizons, diplomatie internationale, interculturalité, construire des projets inter-organisations"
}

pilier_icons = {
    "Développement individuel": ("🟫", "Individu en progression", "#765358"),
    "Entreprise": ("⬜", "Esprit d'Entreprise", "#D3D3D3"),
    "Communaute": ("🟧", "Service à la Communauté", "#E17D4F"),
    "Cooperation": ("🟪", "Coopération Internationale", "#8667D6")
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
    value = st.sidebar.slider(
        label="",
        min_value=0,
        max_value=100,
        value=25,
        label_visibility="collapsed",
        key=slider_id
    )
    pref_piliers[p] = value



st.sidebar.markdown("<div style='font-size: 18px; font-weight: bold; margin-bottom: 2px;'>🌍 ... à un niveau :</div>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size: 14px; color: grey;'>La portée de mon engagement <em>(le où ?)</em></span>", unsafe_allow_html=True)
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
                                          format_func=lambda n: niveau_labels.get(n, n),
                                          label_visibility="collapsed")

# Préparation des données
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]
total_opportunities = len(df)

def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

def make_visual(row, i, small=False):
    niveaux_list = [niveau_labels.get(n, n) for n in row["Niveau"]]
    fig = go.Figure()

    # Couleurs pour les piliers
    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=piliers_labels,
        marker=dict(colors=[couleur_pilier_dict[label] for label in piliers_labels]),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False,
        name="Piliers"
    ))

    # Couleurs pour les verbes
    vals, labels, cols = [], [], []
    for j, (col, label) in enumerate(verbe_map.items()):
        val = row.get(col, 0)
        if val > 0:
            vals.append(val)
            labels.append(label)
            cols.append(couleur_verbe_dict[label])

    fig.add_trace(go.Pie(
        values=vals, labels=labels,
        marker=dict(colors=cols),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='none',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False,
        name="Verbes"
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
st.markdown(f"### ")
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], row["Forme"])
        st.markdown(f"#### {picto} — {row['Nom']}")

        # Ajoutez un lien cliquable si l'URL est présente
        if 'Url' in row and pd.notna(row['Url']):
            st.markdown(f"<div style='font-size:14px; color: #444;'><a href='{row['Url']}' target='_blank'>Petite explication de l'opportunité</a></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:14px; color: #444;'>Petite explication de l'opportunité</div>", unsafe_allow_html=True)

        st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{row['Nom']}")

# Opportunités suivantes
if len(df) > 9:
    st.markdown("### 🔍 D'autres opportunités proches de tes critères")
    other = df.iloc[9:19]
    cols = st.columns(2)
    for i, (_, row) in enumerate(other.iterrows()):
        with cols[i % 2]:
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"**{row['Nom']}** *({niveaux_txt})*")

            # Ajoutez un lien cliquable si l'URL est présente
            if 'Url' in row and pd.notna(row['Url']):
                st.markdown(f"<div style='font-size:14px; color: #444;'><a href='{row['Url']}' target='_blank'>Petite explication de l'opportunité</a></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:14px; color: #444;'>Petite explication de l'opportunité</div>", unsafe_allow_html=True)

            st.plotly_chart(make_visual(row, i+1000, small=True), use_container_width=True, key=f"chart_other_{row['Nom']}")
