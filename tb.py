import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title='NBA Dashboard', layout='wide')

# Chargement des données
@st.cache_data
def load_data():
    # Remplacez ce chemin par le chemin réel de votre base de données
    df = pd.read_csv('base_finale.csv')
    return df

# Fonction pour charger les logos des équipes
def load_team_logos(directory='logos_equipes'):
    logos = {}
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                team_name = os.path.splitext(filename)[0]
                logos[team_name] = os.path.join(directory, filename)
    return logos

# Page 1 : Performances Globales des Équipes
def global_team_performance(df, team_logos):
    st.title('🏀 Performances Globales des Équipes')
    
    # Sélection des métriques à comparer
    metrics = st.multiselect(
        'Choisissez les métriques à comparer', 
        ['Points', 'Rebonds', 'Passes décisives', 'Note de jeu'],
        default=['Points']
    )
    
    # Mapping des métriques
    metric_map = {
        'Points': 'pts',
        'Rebonds': 'reb', 
        'Passes décisives': 'ast',
        'Note de jeu': 'net_rating'
    }
    
    # Calcul des moyennes par équipe
    team_stats = df.groupby('team_abbreviation')[
        [metric_map[m] for m in metrics]
    ].mean().reset_index()
    
    # Création de visualisations
    for metric in metrics:
        st.subheader(f'Comparaison - {metric}')
        
        # Tri des équipes
        sorted_teams = team_stats.sort_values(metric_map[metric], ascending=False)
        
        # Création de la figure avec logos
        fig = go.Figure(data=[
            go.Bar(
                x=sorted_teams['team_abbreviation'], 
                y=sorted_teams[metric_map[metric]],
                text=sorted_teams[metric_map[metric]].round(2),
                textposition='auto',
                marker_color='lightblue'
            )
        ])
        fig.update_layout(
            title=f'Classement des Équipes - {metric}',
            xaxis_title='Équipes',
            yaxis_title=metric
        )
        st.plotly_chart(fig)

# Page 2 : Performances des Joueurs par Équipe
def team_players_performance(df, team_logos):
    st.title('👥 Performances des Joueurs')
    
    # Sélection de l'équipe
    teams = sorted(df['team_abbreviation'].unique())
    selected_team = st.selectbox('Choisissez une équipe', teams)
    
    # Filtrage des joueurs de l'équipe
    team_players = df[df['team_abbreviation'] == selected_team]
    
    # Affichage du logo de l'équipe
    if selected_team in team_logos:
        st.image(team_logos[selected_team], width=200)
    
    # Colonnes pour différentes visualisations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Top Marqueurs')
        top_scorers = team_players.nlargest(5, 'pts')
        fig_scorers = px.bar(
            top_scorers, 
            x='player_name', 
            y='pts', 
            title='Top 5 Marqueurs',
            labels={'player_name': 'Joueur', 'pts': 'Points'}
        )
        st.plotly_chart(fig_scorers)
    
    with col2:
        st.subheader('Répartition des Statistiques')
        stat_cols = ['pts', 'reb', 'ast']
        player_stats = team_players[stat_cols].mean()
        fig_stats = px.pie(
            values=player_stats, 
            names=stat_cols, 
            title='Répartition Moyenne des Statistiques'
        )
        st.plotly_chart(fig_stats)
    
    # Tableau détaillé des joueurs
    st.subheader('Détails des Joueurs')
    st.dataframe(team_players[['player_name', 'age', 'pts', 'reb', 'ast']])

# Page 3 : Meilleurs Clubs et Joueurs
def best_teams_and_players(df, team_logos):
    st.title('🏆 Champions et Stars')
    
    # Calcul des meilleurs équipes
    team_performance = df.groupby('team_abbreviation').agg({
        'pts': 'mean',
        'reb': 'mean',
        'ast': 'mean',
        'net_rating': 'mean'
    }).reset_index()
    
    # Meilleure équipe globale
    best_team = team_performance.loc[team_performance['net_rating'].idxmax()]
    st.subheader(f'🥇 Meilleure Équipe : {best_team["team_abbreviation"]}')
    
    if best_team['team_abbreviation'] in team_logos:
        st.image(team_logos[best_team['team_abbreviation']], width=200)
    
    st.write(f"Performance Globale :")
    st.write(f"- Points Moyens : {best_team['pts']:.2f}")
    st.write(f"- Rebonds Moyens : {best_team['reb']:.2f}")
    st.write(f"- Passes Décisives Moyennes : {best_team['ast']:.2f}")
    st.write(f"- Note Nette : {best_team['net_rating']:.2f}")
    
    # Meilleur joueur global
    best_player = df.loc[df['net_rating'].idxmax()]
    st.subheader(f'🌟 Meilleur Joueur : {best_player["player_name"]}')
    st.write(f"Équipe : {best_player['team_abbreviation']}")
    st.write(f"Performance :")
    st.write(f"- Points : {best_player['pts']:.2f}")
    st.write(f"- Rebonds : {best_player['reb']:.2f}")
    st.write(f"- Passes Décisives : {best_player['ast']:.2f}")
    st.write(f"- Note Nette : {best_player['net_rating']:.2f}")

# Configuration du multipage
def main():
    # Chargement des données
    df = load_data()
    team_logos = load_team_logos()
    
    # Sélection de la page
    page = st.sidebar.radio(
        'Navigation', 
        ['Performances Globales', 'Performances par Équipe', 'Champions et Stars']
    )
    
    # Routing des pages
    if page == 'Performances Globales':
        global_team_performance(df, team_logos)
    elif page == 'Performances par Équipe':
        team_players_performance(df, team_logos)
    else:
        best_teams_and_players(df, team_logos)

# Exécution de l'application
if __name__ == '__main__':
    main()