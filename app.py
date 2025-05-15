import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement local du fichier CSV
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

# Titre + explication reformulée avec carrés
st.markdown("<h1>🗺️ Cartographie des opportunités de la Jeune Chambre</h1>", unsafe_allow_html=True)
st.markdown("""
Cette cartographie t’aide à découvrir les opportunités de la Jeune Chambre Économique qui correspondent à tes envies d'engagement. En bougeant les curseurs à gauche, tu fais ressortir celles qui te ressemblent. 
Tu y retrouves en un coup d'oeil : 
- Le ou les niveaux d'action au centre du visuel 
- Les pictogrammes du type d'opportunité : 🎓 Formation / 🎫 Événement / 🤝 Équipe / 🧪 Programme et initiatives / 🥇 Concours / 🛠️ Projet et action
- **Ce que tu souhaites développer** : le cercle interieur des piliers JCI <span style="color:#A52A2A">🟫 Individu</span> <span style="color:#808080">⬜ Entreprise</span> <span style="color:#FFA500">🟧 Communauté</span> <span style="color:#800080">🟪 International</span>  
- **Comment tu préfères t'impliquer** : le cercle extérieur : <span style="color:#0000FF">🟦 Apprendre</span> <span style="color:#FFD700">🟨 Célébrer</span> <span style="color:#FF0000">🟥 Prendre des responsabilités</span> <span style="color:#28A745">🟩 Se rencontrer</span>
""", unsafe_allow_html=True)

# Filtrage utilisateur
st.sidebar.markdown("### 💓 Ce qui me fait vibrer c'est ...")
pref_engagements = {k: st.sidebar.slider(v, 0, 100, 25, key=f"verb_{k}", help="xxxx") for k, v in verbe_map.items()}

st.sidebar.markdown("### 🧩 ... sous la forme principale de :")
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: f"<span style='background-color:#f0f0f0;padding:2px'>{forme_emojis.get(f, f)}</span>",
                                         label_visibility="collapsed",
                                         help="xxxx")

st.sidebar.markdown("### 🎯 Je souhaite développer ...")
pref_piliers = {p: st.sidebar.slider(p, 0, 100, 25, key=f"pilier_{p}", help="xxxx")
                for p in ["Individu", "Entreprise", "Communaute", "Cooperation"]}

st.sidebar.markdown("### 🌍 ... à un niveau :")
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
                                          format_func=lambda n: f"<span style='background-color:#f0f0f0;padding:2px'>{niveau_labels.get(n, n)}</span>",
                                          label_visibility="collapsed",
                                          help="xxxx")

# === Filtrage ===
df = df[df["Forme"].isin(formes_selected)]
df = df[df["NIVEAU"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    s_verbes = sum((row.get(v, 0) - pref_verbes[v]) ** 2 for v in pref_verbes)
    s_piliers = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_verbes + s_piliers) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# === Affichage ===
def make_visual(row, i, small=False):
    niveaux_list = [niveau_labels.get(n, n) for n in row["NIVEAU"]]
    fig = go.Figure()

    # Piliers
    fig.add_trace(go.Pie(
        values=[row[k] for k in pilier_labels],
        labels=list(pilier_labels.values()),
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none', hoverinfo='label', showlegend=False
    ))

    # Verbes
    fig.add_trace(go.Pie(
        values=[row[v] for v in verbe_labels],
        labels=list(verbe_labels.values()),
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='none', hoverinfo='label', showlegend=False
    ))

    if not small:
        for j, txt in enumerate(niveaux_list):
            fig.add_annotation(text=f"<span style='background-color:#f0f0f0;padding:5px 8px;border-radius:4px;border:1px solid #999'>{txt}</span>",
                               showarrow=False, font=dict(size=11), x=0.5, y=0.5 - j * 0.09,
                               xanchor='center', yanchor='middle')

    fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=260 if not small else 180)
    return fig

# === Résultats ===
st.markdown("### 🌟 Tes opportunités les plus proches")
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        st.markdown(f"#### {forme_emojis.get(row['Forme'], row['Forme'])} — {row['Opportunités']}")
        st.plotly_chart(make_visual(row, i), use_container_width=True)

if len(df) > 9:
    st.markdown("### 🔍 D'autres opportunités ")
    other = df.iloc[9:19]
    cols = st.columns(2)
    for i, (_, row) in enumerate(other.iterrows()):
        with cols[i % 2]:
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["NIVEAU"]])
            st.markdown(f"**{row['Opportunités']}** *({niveaux_txt})*")
            st.plotly_chart(make_visual(row, i+1000, small=True), use_container_width=True)
