import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from PIL import Image

# Configuration de la page avec un thème plus moderne
st.set_page_config(
    page_title='NBA Dashboard 2025',
    layout='wide',
    initial_sidebar_state='expanded',
    page_icon='🏀'
)

# Styles CSS personnalisés pour une apparence soignée
st.markdown("""
    <style>
    .main {background-color: #f5f6f5;}
    .sidebar .sidebar-content {background-color: #1a1a2e;}
    h1 {color: #ff5733; font-family: 'Arial', sans-serif;}
    h2 {color: #2e86c1; font-family: 'Arial', sans-serif;}
    .stButton>button {background-color: #ff5733; color: white;}
    </style>
    """, unsafe_allow_html=True)

# Chargement des données avec gestion des erreurs
@st.cache_data(ttl=600)  # Correction ici : utilisation de ttl au lieu de show_time_to_expire
def load_data():
    try:
        df = pd.read_csv('base_finale.csv')
        return df
    except FileNotFoundError:
        st.error("Erreur : Le fichier 'base_finale.csv' est introuvable.")
        return pd.DataFrame()

# Chargement des logos avec gestion des erreurs
def load_team_logos(directory='logos_equipes'):
    logos = {}
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                team_name = os.path.splitext(filename)[0].upper()
                logos[team_name] = os.path.join(directory, filename)
    return logos

# Page 1 : Performances Globales des Équipes
def global_team_performance(df, team_logos):
    st.title('🏀 Performances Globales des Équipes')
    st.markdown("Analysez les statistiques globales des équipes NBA.")
    
    # Sélection des métriques avec un style amélioré
    metrics = st.multiselect(
        '📊 Choisissez les métriques à comparer',
        ['Points', 'Rebonds', 'Passes décisives', 'Note de jeu'],
        default=['Points'],
        help="Sélectionnez une ou plusieurs métriques pour comparer les équipes."
    )
    
    metric_map = {'Points': 'pts', 'Rebonds': 'reb', 'Passes décisives': 'ast', 'Note de jeu': 'net_rating'}
    team_stats = df.groupby('team_abbreviation')[[metric_map[m] for m in metrics]].mean().reset_index()
    
    for metric in metrics:
        st.subheader(f'📈 {metric} par Équipe')
        sorted_teams = team_stats.sort_values(metric_map[metric], ascending=False)
        
        # Barres avec gradient et hover amélioré
        fig = go.Figure(data=[
            go.Bar(
                x=sorted_teams['team_abbreviation'],
                y=sorted_teams[metric_map[metric]],
                text=sorted_teams[metric_map[metric]].round(2),
                textposition='outside',
                marker=dict(color=sorted_teams[metric_map[metric]], colorscale='Blues'),
                hovertemplate='%{x}: %{y:.2f}<extra></extra>'
            )
        ])
        fig.update_layout(
            title=f'Classement - {metric}',
            xaxis_title='Équipes',
            yaxis_title=metric,
            template='plotly_white',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

# Page 2 : Performances des Joueurs par Équipe
def team_players_performance(df, team_logos):
    st.title('👥 Performances des Joueurs')
    st.markdown("Explorez les performances des joueurs par équipe.")
    
    teams = sorted(df['team_abbreviation'].unique())
    selected_team = st.selectbox('🏟️ Choisissez une équipe', teams, format_func=lambda x: x.upper())
    
    team_players = df[df['team_abbreviation'] == selected_team]
    
    # Affichage du logo avec une animation
    if selected_team in team_logos:
        st.image(team_logos[selected_team], width=150, caption=f"Logo {selected_team}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('🏅 Top 5 Marqueurs')
        top_scorers = team_players.nlargest(5, 'pts')
        fig_scorers = px.bar(
            top_scorers,
            x='player_name',
            y='pts',
            color='pts',
            color_continuous_scale='Teal',
            title='Top 5 Marqueurs',
            labels={'player_name': 'Joueur', 'pts': 'Points'},
            text=top_scorers['pts'].round(1)
        )
        fig_scorers.update_traces(textposition='outside')
        fig_scorers.update_layout(showlegend=False)
        st.plotly_chart(fig_scorers, use_container_width=True)
    
    with col2:
        st.subheader('📊 Répartition des Stats')
        stat_cols = ['pts', 'reb', 'ast']
        player_stats = team_players[stat_cols].mean()
        fig_stats = px.pie(
            values=player_stats,
            names=['Points', 'Rebonds', 'Passes'],
            title='Moyenne des Statistiques',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_stats.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_stats, use_container_width=True)
    
    st.subheader('📋 Détails des Joueurs')
    styled_df = team_players[['player_name', 'age', 'pts', 'reb', 'ast']].style.format({'pts': '{:.1f}', 'reb': '{:.1f}', 'ast': '{:.1f}'})
    st.dataframe(styled_df, use_container_width=True)

# Page 3 : Meilleurs Clubs et Joueurs
def best_teams_and_players(df, team_logos):
    st.title('🏆 Champions et Stars')
    st.markdown("Découvrez les meilleures équipes et joueurs selon leurs performances.")
    
    team_performance = df.groupby('team_abbreviation').agg({
        'pts': 'mean', 'reb': 'mean', 'ast': 'mean', 'net_rating': 'mean'
    }).reset_index()
    
    best_team = team_performance.loc[team_performance['net_rating'].idxmax()]
    st.subheader(f'🥇 Meilleure Équipe : {best_team["team_abbreviation"]}')
    
    if best_team['team_abbreviation'] in team_logos:
        st.image(team_logos[best_team['team_abbreviation']], width=150)
    
    st.metric("Points Moyens", f"{best_team['pts']:.2f}")
    st.metric("Rebonds Moyens", f"{best_team['reb']:.2f}")
    st.metric("Passes Décisives", f"{best_team['ast']:.2f}")
    st.metric("Note Nette", f"{best_team['net_rating']:.2f}")
    
    best_player = df.loc[df['net_rating'].idxmax()]
    st.subheader(f'🌟 Meilleur Joueur : {best_player["player_name"]}')
    st.write(f"**Équipe** : {best_player['team_abbreviation']}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Points", f"{best_player['pts']:.2f}")
        st.metric("Rebonds", f"{best_player['reb']:.2f}")
    with col2:
        st.metric("Passes Décisives", f"{best_player['ast']:.2f}")
        st.metric("Note Nette", f"{best_player['net_rating']:.2f}")

# Sidebar améliorée
def main():
    df = load_data()
    if df.empty:
        st.stop()
    
    team_logos = load_team_logos()
    
    st.sidebar.image("https://cdn.nba.com/manage/2021/08/nba-logo.jpg", width=150)
    st.sidebar.title("🏀 NBA Dashboard")
    page = st.sidebar.radio(
        'Navigation',
        ['Performances Globales', 'Performances par Équipe', 'Champions et Stars'],
        label_visibility='collapsed'
    )
    
    if page == 'Performances Globales':
        global_team_performance(df, team_logos)
    elif page == 'Performances par Équipe':
        team_players_performance(df, team_logos)
    else:
        best_teams_and_players(df, team_logos)

if __name__ == '__main__':
    main()