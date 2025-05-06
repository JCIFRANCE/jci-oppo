
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Emojis et couleurs
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
niveau_labels = {"L": "🏘️ Local", "R": "🏙️ Régional", "N": "🇫🇷 National", "Z": "🌍 Zone", "M": "🌐 Monde"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

couleurs_verbes = ["#FF4B4B", "#4B6CFF", "#28A745", "#FF9900"]
couleurs_piliers = ["#FFC0CB", "#B0E0E6", "#FFFACD", "#D8BFD8"]

# Texte descriptif
st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités")

with st.container():
    st.markdown("""
    <div style="position: sticky; top: 0; background-color: white; z-index: 999; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
    <h4>📍 Légende</h4>
    <ul style="margin-left: 1em;">
        <li><strong>Les verbes</strong> (donut) : 
            <span title="Acquérir des compétences, découvrir de nouvelles approches ou outils">🟥 Apprendre</span>,
            <span title="Mettre à l'honneur, valoriser des actions ou des personnes">🟦 Célébrer</span>,
            <span title="Assumer un rôle ou une mission avec impact">🟩 Prendre des responsabilités</span>,
            <span title="Créer du lien humain, rencontrer des acteurs variés">🟧 Se rencontrer</span>.
        </li>
        <li><strong>Les piliers</strong> (centre dégradé) : 
            <span title="Développement personnel et leadership">🎯 Individu</span>,
            <span title="Compétences entrepreneuriales et professionnelles">💼 Entreprise</span>,
            <span title="Engagement local ou sociétal">🏘️ Communauté</span>,
            <span title="Ouverture au monde et aux cultures">🌐 International</span>.
        </li>
    </ul>
    <p>🔎 Utilisez les filtres à gauche pour personnaliser les opportunités affichées selon vos envies.</p>
    </div>
    """, unsafe_allow_html=True)

# Filtres
with st.sidebar:
    st.markdown("### 🎯 Je recherche une opportunité...")
    formes = sorted(df["Forme"].unique().tolist())
    formes_selected = st.multiselect(
        "🔸 ... sous la forme principale de",
        options=formes,
        default=formes,
        format_func=lambda f: forme_emojis.get(f, f"📌 {f}"),
        label_visibility="visible",
        key="formats"
    )

    niveaux = ["L", "R", "N", "Z", "M"]
    niveaux_selected = st.multiselect(
        "🌍 ... au niveau",
        options=niveaux,
        default=niveaux,
        format_func=lambda n: niveau_labels.get(n, n),
        label_visibility="visible",
        key="niveaux"
    )

    st.markdown("### 🧭 ... qui me permettra de :")
    pref_engagements = {}
    for verbe in ["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"]:
        st.markdown("<div style='margin-bottom:-18px;'></div>", unsafe_allow_html=True)
        pref_engagements[verbe] = st.slider(verbe, 0, 100, 25)

    st.markdown("### 🌐 ... avec un impact sur :")
    pref_piliers = {}
    for pilier in ["Individu", "Entreprise", "Communaute", "Cooperation"]:
        st.markdown("<div style='margin-bottom:-18px;'></div>", unsafe_allow_html=True)
        pref_piliers[pilier] = st.slider(pilier, 0, 100, 25)

# Filtrage
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

# Scoring
def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Visu
def make_visual(row):
    fig = go.Figure()

    # Centre : piliers
    fig.add_trace(go.Pie(
        values=[row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]],
        labels=["Individu", "Entreprise", "Communauté", "International"],
        marker=dict(colors=couleurs_piliers),
        hole=0.3,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        textinfo='none',
        showlegend=False
    ))

    # Extérieur : verbes
    fig.add_trace(go.Pie(
        values=[
            row["Apprendre"],
            row["Célébrer"],
            row["Prendre des responsabilités"],
            row["Se rencontrer"]
        ],
        labels=["Apprendre", "Célébrer", "Prendre des responsabilités", "Se rencontrer"],
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textposition='inside',
        textinfo='label',
        showlegend=False
    ))

    fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=420)
    return fig

# Affichage
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
        st.plotly_chart(make_visual(row), use_container_width=True)
