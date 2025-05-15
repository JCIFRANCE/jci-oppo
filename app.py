import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    "Programme": "🧪 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
}
couleurs_verbes = ["#0000FF", "#FFD700", "#FF0000", "#28A745"]
couleurs_piliers = ["#A52A2A", "#808080", "#FFA500", "#800080"]
verbes_labels = ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]
piliers_labels = ["Individu", "Entreprise", "Communauté", "International"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.markdown("""
<style>
/* Réduction marges sliders */
section[data-testid="stSidebar"] .stSlider {
    margin-top: -10px;
    margin-bottom: 4px;
}

/* Cacher les ticks (0 / 100) sous les sliders */
section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"] {
    display: none;
}

/* Cacher les bulles de valeur (Streamlit les rend dynamiquement dans une div positionnée en absolu) */
section[data-testid="stSidebar"] .stSlider > div > div > div[role="slider"]::after {
    content: none !important;
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


# Titre + explication reformulée avec carrés
st.markdown("<h1>🗺️ Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)
st.markdown("""
Cette cartographie t’aide à découvrir les opportunités de la Jeune Chambre Économique qui correspondent à tes envies d'engagement. En bougeant les curseurs à gauche, tu fais ressortir celles qui te ressemblent. 
Tu y retrouves en un coup d'oeil : 
- Le ou les niveaux d'action au centre du visuel : Local / Régional / National / Zone / Mondial
- Les pictogrammes du type d'opportunité : 🎓 Formations et ateliers / 🎫 Événements / 🤝 En Équipe / 🧪 Programmes et initiatives / 🥇 Concours / 🛠️ Projets et actions
- **Ce que tu souhaites développer** : le cercle intérieur des piliers JCI <span style="color:#A52A2A">🟫 Développement personnel (pilier "Individu")</span> <span style="color:#808080">⬜ Compétences professionnelles et entrepreneuriales (pilier "Business")</span> <span style="color:#FFA500">🟧 Service au territoire ( pilier "Communauté")</span> <span style="color:#800080">🟪 Coopération internationale (pilier "International")</span>  
- **Comment tu préfères t'impliquer** : le cercle extérieur : <span style="color:#0000FF">🟦 Apprendre</span> <span style="color:#FFD700">🟨 Célébrer</span> <span style="color:#FF0000">🟥 Prendre des responsabilités</span> <span style="color:#28A745">🟩 Se rencontrer</span>
""", unsafe_allow_html=True)

# Filtrage utilisateur
st.sidebar.markdown("## 🗺️ Découvre les opportunités JCE/JCI qui correspondent à ton style d'engagement")

import streamlit.components.v1 as components

st.sidebar.markdown("### 💓 Ce qui me fait vibrer c'est ...")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Ma préférence d'engagement : le <em>comment</em></span>", unsafe_allow_html=True)

verbes_circulaires = [
    ("🟦", "Apprendre", "#0000FF", "circular_slider_apprendre"),
    ("🟨", "Célébrer", "#FFD700", "circular_slider_celebrer"),
    ("🟥", "Prendre des responsabilités", "#FF0000", "circular_slider_responsabiliser"),
    ("🟩", "Se rencontrer", "#28A745", "circular_slider_rencontrer")
]

for emoji, label, color, slider_id in verbes_circulaires:
    st.sidebar.markdown(f"#### {emoji} {label}")

    components.html(f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 200px;">
      <div id="{slider_id}_container" style="position: relative; width: 150px; height: 150px;">
        <input id="{slider_id}" type="range" min="0" max="100" value="25"
          style="
            position: absolute;
            width: 150px;
            height: 150px;
            border-radius: 50%;
            transform: rotate(-90deg);
            opacity: 0;
            z-index: 2;
            cursor: pointer;
          " oninput="document.getElementById('{slider_id}_value').innerText = this.value; update_{slider_id}(this.value);" />
        
        <svg width="150" height="150" style="position: absolute; top: 0; left: 0;">
          <circle cx="75" cy="75" r="65" stroke="#eee" stroke-width="12" fill="none" />
          <circle id="{slider_id}_progress" cx="75" cy="75" r="65" stroke="{color}" stroke-width="12" fill="none"
            stroke-dasharray="408.4"
            stroke-dashoffset="306.3"
            transform="rotate(-90 75 75)"
          />
        </svg>

        <div id="{slider_id}_value" style="
          position: absolute;
          width: 100%;
          top: 50%;
          left: 0;
          transform: translateY(-50%);
          text-align: center;
          font-size: 18px;
          font-weight: bold;
          color: {color};
          z-index: 1;
        ">25</div>
      </div>
    </div>

    <script>
      function update_{slider_id}(value) {{
        const max = 100;
        const percent = value / max;
        const offset = 408.4 - percent * 408.4;
        document.getElementById('{slider_id}_progress').style.strokeDashoffset = offset;
      }}
    </script>
    """, height=220)

   
st.sidebar.markdown("### 🧩 ... sous la forme principale de :")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>La forme de mon engagement : le <em>quoi</em></span>", unsafe_allow_html=True)
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: forme_emojis.get(f, f),
                                         label_visibility="collapsed")

st.sidebar.markdown("### 🎯 Je souhaite développer ...")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Les 4 piliers JCI = les raisons de mon engagement : le <em>pourquoi</em></span>", unsafe_allow_html=True)
pilier_icons = {
    "Développement individuel": ("🟫", "Individu"),
    "Entreprise": ("⬜", "Entreprise"),
    "Communaute": ("🟧", "Communauté"),
    "Cooperation": ("🟪", "International")
}

# PILIERS : symbole + label + couleur
pilier_icons = {
    "Développement individuel": ("🟫", "Individu", "#A52A2A"),
    "Entreprise": ("⬜", "Entreprise", "#808080"),
    "Communaute": ("🟧", "Communauté", "#FFA500"),
    "Cooperation": ("🟪", "International", "#800080")
}

pref_piliers = {}
for p, (emoji, label, color) in pilier_icons.items():
    st.sidebar.markdown(f"<span style='font-weight: 500;'>{emoji} {label}</span>", unsafe_allow_html=True)
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
 


st.sidebar.markdown("### 🌍 ... à un niveau :")
st.sidebar.markdown("<span style='font-size: 11px; color: grey;'>Quelle portée a mon engagement : le <em>où</em></span>", unsafe_allow_html=True)
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
st.markdown (f"### ")
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
