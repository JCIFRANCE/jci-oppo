
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Mapping entre noms internes et affichés
verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}

# Couleurs mises à jour
couleurs_verbes = ["#0000FF", "#FFD700", "#FF0000", "#28A745"]  # bleu, jaune, rouge, vert
couleurs_piliers = ["#A52A2A", "#808080", "#FFA500", "#800080"]  # marron, gris, orange, violet

# Infos
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
niveau_labels = {"L": "🏘️ Local", "R": "🏙️ Régional", "N": "🇫🇷 National", "Z": "🌍 Zone", "M": "🌐 Monde"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités")

# Légende avec couleurs et descriptions
with st.container():
    st.markdown("""
    <div style="position: sticky; top: 0; background-color: white; z-index: 999; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
    <h4>📍 Légende</h4>
    <ul>
        <li><strong>Verbes (donut)</strong> :
            <span style="color:#0000FF" title="Acquérir des compétences, découvrir de nouvelles approches ou outils">🟦 Apprendre</span>,
            <span style="color:#FFD700" title="Mettre à l'honneur, valoriser des actions ou des personnes">🟨 Célébrer</span>,
            <span style="color:#FF0000" title="Assumer un rôle ou une mission avec impact">🟥 Prendre des responsabilités</span>,
            <span style="color:#28A745" title="Créer du lien humain, rencontrer des acteurs variés">🟩 Se rencontrer</span>.
        </li>
        <li><strong>Piliers (centre)</strong> :
            <span style="color:#A52A2A" title="Développement personnel et leadership">🟫 Individu</span>,
            <span style="color:#808080" title="Compétences entrepreneuriales et professionnelles">⬜ Entreprise</span>,
            <span style="color:#FFA500" title="Engagement local ou sociétal">🟧 Communauté</span>,
            <span style="color:#800080" title="Ouverture au monde et aux cultures">🟪 International</span>.
        </li>
    </ul>
    <p>🔎 Utilisez les filtres à gauche pour personnaliser les opportunités affichées selon vos envies.</p>
    </div>
    """, unsafe_allow_html=True)

# Barre latérale optimisée
st.sidebar.markdown("<style>.css-1d391kg {width: 380px !important;}</style>", unsafe_allow_html=True)
st.sidebar.markdown("### 🧭 Je souhaite une opportunité qui me permet de :")
pref_engagements = {}
for col, label in verbe_map.items():
    st.sidebar.markdown("<div style='margin-bottom:-18px;'></div>", unsafe_allow_html=True)
    pref_engagements[col] = st.sidebar.slider(label, 0, 100, 25, key=f"verb_{col}")

st.sidebar.markdown("### 🔸 ... sous la forme de :")
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect(
    "Formats", options=formes, default=formes,
    format_func=lambda f: forme_emojis.get(f, f"📌 {f}"),
    label_visibility="collapsed"
)

st.sidebar.markdown("### 🌍 ... au niveau :")
niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect(
    "Niveaux", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n),
    label_visibility="collapsed"
)

st.sidebar.markdown("### 🌐 ... avec un impact sur :")
pref_piliers = {}
for pilier in ["Individu", "Entreprise", "Communaute", "Cooperation"]:
    st.sidebar.markdown("<div style='margin-bottom:-18px;'></div>", unsafe_allow_html=True)
    pref_piliers[pilier] = st.sidebar.slider(pilier, 0, 100, 25, key=f"pilier_{pilier}")

# Filtrage
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    s_eng = sum((row.get(k, 0) - pref_engagements[k]) ** 2 for k in pref_engagements)
    s_pil = sum((row.get(k, 0) - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (s_eng + s_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Visualisation combinée
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

    # Donut externe : verbes
    fig.add_trace(go.Pie(
        values=[row[k] for k in verbe_map.keys()],
        labels=[verbe_map[k] for k in verbe_map.keys()],
        marker=dict(colors=couleurs_verbes),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textposition='inside',
        textinfo='label',
        showlegend=False
    ))

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=400)
    return fig

# Affichage sécurisé
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        try:
            picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
            niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
            st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
            st.plotly_chart(make_visual(row), use_container_width=True, key=f"chart_{i}")
        except Exception:
            st.error("❌ Erreur lors de l’affichage de cette opportunité.")
