

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités")

st.markdown("""
<style>
.sticky-header {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 999;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}
</style>
<div class="sticky-header">
<h4>📍 Légende</h4>
<ul>
    <li><strong>Verbes (donut)</strong> :
        <span style="color:#0000FF">🟦 Apprendre</span>,
        <span style="color:#FFD700">🟨 Célébrer</span>,
        <span style="color:#FF0000">🟥 Prendre des responsabilités</span>,
        <span style="color:#28A745">🟩 Se rencontrer</span>.
    </li>
    <li><strong>Piliers JCI (centre)</strong> :
        <span style="color:#A52A2A">🟫 Individu</span>,
        <span style="color:#808080">⬜ Entreprise</span>,
        <span style="color:#FFA500">🟧 Communauté</span>,
        <span style="color:#800080">🟪 International</span>.
    </li>
</ul>
<p>🔎 Utilise les curseurs et les sélections à gauche pour découvrir les opportunités qui te ressemblent !</p>
</div>
""", unsafe_allow_html=True)

# Sélection
st.sidebar.markdown("### 🎯 Je recherche les opportunités Jeune Chambre qui me permettront de ...")
pref_engagements = {k: st.sidebar.slider(v, 0, 100, 25, key=f"verb_{k}") for k, v in verbe_map.items()}

st.sidebar.markdown("### 🧩 ... sous la forme principale de :")
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: forme_emojis.get(f, f),
                                         label_visibility="collapsed",
                                         placeholder="Choisis un ou plusieurs formats")

st.sidebar.markdown("### 🌍 ... à un niveau :")
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
                                          format_func=lambda n: niveau_labels.get(n, n),
                                          label_visibility="collapsed",
                                          placeholder="Choisis un ou plusieurs niveaux")

st.sidebar.markdown("### 🌐 ... qui correspond au pilier JCI :")
pref_piliers = {p: st.sidebar.slider(p, 0, 100, 25, key=f"pilier_{p}")
                for p in ["Individu", "Entreprise", "Communaute", "Cooperation"]}

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
    levels = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=["Individu", "Entreprise", "Communauté", "International"],
        marker=dict(colors=couleurs_piliers),
        hole=0.3, domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none', showlegend=False
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
        hole=0.6, domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='label' if not small else 'none',
        textposition='inside',
        insidetextorientation='radial',
        hovertemplate='<b>%{label}</b><extra></extra>',
        showlegend=False
    ))

    if not small:
        fig.add_annotation(text=levels, showarrow=False,
                           font=dict(size=12), x=0.5, y=0.5,
                           xanchor='center', yanchor='middle')
    fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=260 if not small else 180)
    return fig

# Haut de page
st.markdown(f"### Tu vois ici {min(9, len(df))} opportunités sur les {total_opportunities} opportunités qu'offre la Jeune Chambre.")
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], row["Forme"])
        st.markdown(f"#### {picto} — {row['Nom']}")
        st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{i}")

# Suggestions
if len(df) > 9:
    st.markdown("### 🔍 D'autres opportunités proches de tes critères")
    other = df.iloc[9:19]
    cols = st.columns(2)
    for i, (_, row) in enumerate(other.iterrows()):
        with cols[i % 2]:
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"**{row['Nom']}** *({niveaux_txt})*")
            st.plotly_chart(make_visual(row, i+1000, small=True), use_container_width=True)
