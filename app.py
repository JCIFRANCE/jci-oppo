
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Données
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

# Mappings
verbe_map = {
    "Apprendre": "Apprendre",
    "Célébrer": "Célébrer",
    "Responsabiliser": "Prendre des responsabilités",
    "Rencontrer": "Se rencontrer"
}
niveau_labels = {"L": "Local", "R": "Régional", "N": "National", "Z": "Zone", "M": "Monde"}
forme_emojis = {
    "Programme": "🧪 Programme", 
    "Concours": "🥇 Concours", 
    "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", 
    "Equipe": "🤝 Équipe", 
    "Événement": "🎫 Événement", 
    "Formation": "🎓 Formation"
}

# Couleurs
couleurs_verbes = ["#0000FF", "#FFD700", "#FF0000", "#28A745"]
couleurs_piliers = ["#A52A2A", "#808080", "#FFA500", "#800080"]

st.set_page_config(page_title="Cartographie des opportunités", layout="wide")
st.title("🗺️ Cartographie des opportunités")

# Légende
st.markdown("""
<div style="position: sticky; top: 0; background-color: white; z-index: 999; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
<h4>📍 Légende</h4>
<ul>
    <li><strong>Verbes (donut)</strong> :
        <span style="color:#0000FF">🟦 Apprendre</span>,
        <span style="color:#FFD700">🟨 Célébrer</span>,
        <span style="color:#FF0000">🟥 Prendre des responsabilités</span>,
        <span style="color:#28A745">🟩 Se rencontrer</span>.
    </li>
    <li><strong>Piliers (centre)</strong> :
        <span style="color:#A52A2A">🟫 Individu</span>,
        <span style="color:#808080">⬜ Entreprise</span>,
        <span style="color:#FFA500">🟧 Communauté</span>,
        <span style="color:#800080">🟪 International</span>.
    </li>
</ul>
<p>🔎 Utilisez les filtres à gauche pour personnaliser les opportunités affichées selon vos envies.</p>
</div>
""", unsafe_allow_html=True)

# Filtres
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
    format_func=lambda f: forme_emojis.get(f, f),
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

# Visualisation
def make_visual(row, i):
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

    # Donut externe : verbes avec hover bulle BD
    fig.add_trace(go.Pie(
        values=[row[k] for k in verbe_map.keys()],
        labels=[verbe_map[k] for k in verbe_map.keys()],
        marker=dict(colors=couleurs_verbes, line=dict(color="white", width=2)),
        hole=0.6,
        domain={'x': [0, 1], 'y': [0, 1]},
        textinfo='label',
        hovertemplate='<b style="font-size:16px;">%{label}</b><br>Score : %{value}<extra></extra>',
        showlegend=False
    ))

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=400)
    return fig

# Affichage fixe en grille
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        try:
            picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
            niveaux_txt = ", ".join([niveau_labels.get(n, n) for n in row["Niveau"]])
            st.markdown(f"<div style='height:520px'><h4>{picto} — {row['Nom']} <em style='font-size:90%'>{niveaux_txt}</em></h4>", unsafe_allow_html=True)
            st.plotly_chart(make_visual(row, i), use_container_width=True, key=f"chart_{i}")
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception:
            st.error("❌ Erreur lors de l’affichage de cette opportunité.")
