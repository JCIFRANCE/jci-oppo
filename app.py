
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Données
df = pd.read_csv("data.csv")
df["Forme"] = df["Forme"].str.strip().str.capitalize()
df["Forme"] = df["Forme"].replace({"Autre": "Événement", "Evenement": "Événement"})
df["Niveau"] = df["Niveau"].astype(str).apply(lambda x: [n for n in x if n in "LRNZM"])

# Emojis
niveau_emoji = {"L": "🏘️", "R": "🏙️", "N": "🇫🇷", "Z": "🌍", "M": "🌐"}
niveau_labels = {"L": "🏘️ Local", "R": "🏙️ Régional", "N": "🇫🇷 National", "Z": "🌍 Zone", "M": "🌐 Monde"}
forme_emojis = {
    "Programme": "🧠 Programme", "Concours": "🥇 Concours", "Projet": "🛠️ Projet",
    "Fonction": "👔 Fonction", "Equipe": "🤝 Équipe", "Événement": "🎫 Événement"
}

# Couleurs
couleurs_verbes = ["#FF6666", "#6666FF", "#66CC66", "#FFB266"]
couleurs_piliers = ["#c2f0c2", "#c2d1f0", "#ffe6cc", "#e6ccff"]

st.set_page_config(page_title="Sunburst + Marimekko", layout="wide")
st.title("🌗 Demi-sunburst pour les verbes + Marimekko carré pour les piliers")

# Volet de sélection
formes = sorted(df["Forme"].unique().tolist())
formes_selected = st.sidebar.multiselect(
    "🧩 Formats", options=formes, default=formes,
    format_func=lambda f: forme_emojis.get(f, f"📌 {f}")
)
if not formes_selected:
    st.sidebar.warning("Sélectionnez au moins un format.")
    st.stop()

niveaux = ["L", "R", "N", "Z", "M"]
niveaux_selected = st.sidebar.multiselect(
    "🌍 Niveaux", options=niveaux, default=niveaux,
    format_func=lambda n: niveau_labels.get(n, n)
)
if not niveaux_selected:
    st.sidebar.warning("Sélectionnez au moins un niveau.")
    st.stop()

st.sidebar.markdown("### 🧭 Engagements")
pref_engagements = {
    "Apprendre": st.sidebar.slider("Apprendre", 0, 100, 25),
    "Célébrer": st.sidebar.slider("Célébrer", 0, 100, 25),
    "Responsabiliser": st.sidebar.slider("Responsabiliser", 0, 100, 25),
    "Rencontrer": st.sidebar.slider("Rencontrer", 0, 100, 25),
}

st.sidebar.markdown("### 🌐 Piliers")
pref_piliers = {
    "Individu": st.sidebar.slider("Individu", 0, 100, 25),
    "Entreprise": st.sidebar.slider("Entreprise", 0, 100, 25),
    "Communaute": st.sidebar.slider("Communauté", 0, 100, 25),
    "Cooperation": st.sidebar.slider("International", 0, 100, 25),
}

# Filtrage et score
df = df[df["Forme"].isin(formes_selected)]
df = df[df["Niveau"].apply(lambda lv: any(n in niveaux_selected for n in lv))]

def score(row):
    score_eng = sum((row[k] - pref_engagements[k]) ** 2 for k in pref_engagements)
    score_pil = sum((row[k] - pref_piliers[k]) ** 2 for k in pref_piliers)
    return (score_eng + score_pil) ** 0.5

df["Score"] = df.apply(score, axis=1)
df = df.sort_values("Score").reset_index(drop=True)

# Fonction graphique
def make_diagrams(row):
    # Demi-sunburst
    labels = ["", "Apprendre", "Célébrer", "Responsabiliser", "Rencontrer"]
    parents = ["", "", "", "", ""]
    values = [0, row["Apprendre"], row["Célébrer"], row["Responsabiliser"], row["Rencontrer"]]
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=["white"] + couleurs_verbes),
        insidetextorientation='radial',
        maxdepth=2
    ))

    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        sunburstcolorway=couleurs_verbes,
        height=300,
        uniformtext=dict(minsize=10, mode='hide'),
    )

    # Marimekko carré
    total = sum([row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]])
    widths = [row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]]
    widths = [w / total for w in widths]

    base_x = 0.25
    shapes = []
    annotations = []
    for i, w in enumerate(widths):
        x0 = base_x
        x1 = base_x + w * 0.5
        shapes.append(dict(
            type="rect",
            xref="paper", yref="paper",
            x0=x0, x1=x1,
            y0=0.0, y1=0.2,
            fillcolor=couleurs_piliers[i],
            line=dict(width=0)
        ))
        annotations.append(dict(
            x=(x0 + x1) / 2, y=0.1,
            xref="paper", yref="paper",
            text=["Individu", "Entreprise", "Communauté", "International"][i],
            showarrow=False,
            font=dict(size=10)
        ))
        base_x += w * 0.5

    fig.update_layout(shapes=shapes, annotations=annotations)

    return fig

# Affichage
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
        st.plotly_chart(make_diagrams(row), use_container_width=True)
