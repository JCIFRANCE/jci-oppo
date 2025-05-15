
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# === Chargement des données ===
url = "https://drive.google.com/uc?export=download&id=1cQxjIyK3LjuoNNK58Mm4BRbhb6uv7nES"
df = pd.read_csv(url, sep=';', skiprows=5, encoding='utf-8-sig')

# Nettoyage des colonnes
df.columns = df.columns.str.strip()
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["NIVEAU"] = df["NIVEAU"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Dictionnaires de correspondance
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement", "Formation": "🎓 Formation"
}

# Libellés affichés pour les sliders
verbe_labels = {
    "Apprendre": "🔵 Apprendre",
    "Prendre des responsabilités": "🔴 Prendre des responsabilités",
    "Célébrer": "🟡 Célébrer",
    "Se rencontrer": "🟢 Se rencontrer"
}
pilier_labels = {
    "Individu": "🌐 Développement individuel",
    "Entreprise": "💼 Entreprise",
    "International": "🌍 Coopération internationale",
    "Communauté": "🏢 Service à la communauté"
}

couleurs_verbes = ["#0000FF", "#FF0000", "#FFD700", "#28A745"]
couleurs_piliers = ["#A52A2A", "#808080", "#800080", "#FFA500"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités JCEF")

# === Filtres ===
st.sidebar.markdown("### 💗 Ce que j'aime faire")
pref_verbes = {v: st.sidebar.slider(verbe_labels[v], 0, 100, 25) for v in verbe_labels}

st.sidebar.markdown("### 🎯 Je souhaite développer")
pref_piliers = {k: st.sidebar.slider(pilier_labels[k], 0, 100, 25) for k in pilier_labels}

st.sidebar.markdown("### 🌍 Niveau d'engagement")
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect("", options=niveaux, default=niveaux,
                                          format_func=lambda n: niveau_labels[n], label_visibility="collapsed")

formes = sorted(df["Forme"].dropna().unique().tolist())
st.sidebar.markdown("### 📊 Type d'opportunité")
formes_selected = st.sidebar.multiselect("", options=formes, default=formes,
                                         format_func=lambda f: forme_emojis.get(f, f),
                                         label_visibility="collapsed")

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
