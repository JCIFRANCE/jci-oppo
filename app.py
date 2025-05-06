
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

st.set_page_config(page_title="Sunburst semi-circulaire + barres", layout="wide")
st.title("🌗 Sunburst demi-cercle pour les verbes + barres nettes pour les piliers")

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

# Fonction graphique combinée
def make_sunburst_and_bars(row):
    fig = go.Figure()

    # 4 segments de 45° chacun dans la demi-rosace
    verbes = [("Apprendre", 0), ("Célébrer", 45), ("Responsabiliser", 90), ("Rencontrer", 135)]
    for i, (verbe, angle) in enumerate(verbes):
        level = row[verbe]
        fig.add_trace(go.Barpolar(
            r=[level],
            theta=[angle],
            width=[45],
            marker=dict(color=couleurs_verbes[i], opacity=min(0.3 + level / 100, 1)),
            text=f"{verbe} : {level}",
            hoverinfo="text"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(showline=False, showticklabels=False)
        ),
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        showlegend=False
    )

    # Enchaînement avec les piliers
    pilier_labels = ["Individu", "Entreprise", "Communauté", "International"]
    pilier_values = [row["Individu"], row["Entreprise"], row["Communaute"], row["Cooperation"]]
    bar_fig = go.Figure(go.Bar(
        x=pilier_labels,
        y=pilier_values,
        marker_color=couleurs_piliers,
        text=pilier_values,
        textposition="auto"
    ))

    bar_fig.update_layout(
        height=200,
        margin=dict(t=0, b=40, l=40, r=40),
        showlegend=False,
        yaxis=dict(range=[0, 100])
    )

    return fig, bar_fig

# Affichage
top = df.head(9)
cols = st.columns(3)
for i, (_, row) in enumerate(top.iterrows()):
    with cols[i % 3]:
        picto = forme_emojis.get(row["Forme"], f"📌 {row['Forme']}")
        niveaux_str = " ".join([niveau_emoji.get(n, "") for n in row["Niveau"]])
        st.markdown(f"### {picto} — {row['Nom']} {niveaux_str}")
        polar_fig, bars_fig = make_sunburst_and_bars(row)
        st.plotly_chart(polar_fig, use_container_width=True)
        st.plotly_chart(bars_fig, use_container_width=True)
