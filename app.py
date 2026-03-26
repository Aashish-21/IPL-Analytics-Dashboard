import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ── Page config ──────────────────────────────────────────
st.set_page_config(page_title="IPL Analytics Dashboard", page_icon="🏏", layout="wide")

# ── Custom CSS for IPL Theme & Visibility ────────────────
st.markdown("""
    <style>
    /* Remove white space at the top */
    header {
        visibility: hidden;
        height: 0px !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    /* Main Background */
    .stApp {
        background-color: #001C58;
        color: white;
    }
    
    /* Adjust top padding of main content */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #000F2E;
        border-right: 2px solid #FFD700;
    }
    
    /* Fix Visibility of Sidebar Text & Widgets */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {
        color: #FFD700 !important;
        font-weight: bold;
    }
    
    /* Enhance Multi-select and Selectbox appearance */
    .stMultiSelect, .stSelectbox {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid #FFD700;
    }
    
    /* Change color of selected filter tags to align with theme */
    span[data-baseweb="tag"] {
        background-color: #FFD700 !important;
        color: #001C58 !important;
        border-radius: 4px !important;
    }
    
    /* Fix Widget labels */
    label[data-testid="stWidgetLabel"] {
        color: #FFD700 !important;
    }

    /* Card / Container Styling */
    div.stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-bottom: 5px solid #FFD700;
        overflow: hidden;
    }
    
    /* Metric Text Adjustment */
    [data-testid="stMetricValue"] {
        color: #001C58 !important;
        font-size: 1.6rem !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
    }

    /* Headlines */
    h1, h2, h3 {
        color: #FFD700 !important;
        font-family: 'Trebuchet MS', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #000F2E;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #FFD700 !important;
        border-bottom-color: #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Load & clean data ─────────────────────────────────────
@st.cache_data
def load_data():
    try:
        matches = pd.read_csv('data/matches.csv')
        deliveries = pd.read_csv('data/deliveries.csv')
    except:
        st.error("Please ensure matches.csv and deliveries.csv are in the 'data/' folder.")
        st.stop()
        
    team_name_map = {
        'Delhi Daredevils': 'Delhi Capitals',
        'Kings XI Punjab': 'Punjab Kings',
        'Deccan Chargers': 'Sunrisers Hyderabad',
    }
    for col in ['team1', 'team2', 'winner', 'toss_winner']:
        matches[col] = matches[col].replace(team_name_map)
    for col in ['batting_team', 'bowling_team']:
        deliveries[col] = deliveries[col].replace(team_name_map)
    matches = matches.dropna(subset=['winner'])
    return matches, deliveries

matches, deliveries = load_data()

# ── Sidebar filters ───────────────────────────────────────
st.sidebar.image("https://crystalpng.com/wp-content/uploads/2025/09/ipl-logo.png", width=120)
st.sidebar.markdown("### Global Filters")
all_seasons = sorted(matches['season'].unique())
selected_seasons = st.sidebar.multiselect("📅 Select Season(s)", all_seasons, default=all_seasons)

if not selected_seasons:
    st.warning("Please select at least one season.")
    st.stop()

filtered_matches = matches[matches['season'].isin(selected_seasons)]
filtered_deliveries = deliveries[deliveries['match_id'].isin(filtered_matches['id'])]

# ── Header ────────────────────────────────────────────────
st.title("🏏 IPL Analytics Dashboard")

# Global Plotting Config
plt.rcParams.update({
    "figure.facecolor": "#001C58", "axes.facecolor": "#001C58", "axes.edgecolor": "#FFD700",
    "axes.labelcolor": "white", "xtick.color": "white", "ytick.color": "white",
    "grid.color": "#1a3a8a", "font.size": 10
})

# ── Tabs Navigation ───────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Tournament Overview", "⚔️ Team vs Team", "👤 Player Spotlight"])

# ──────────────────────────────────────────────────────────
# TAB 1: TOURNAMENT OVERVIEW
# ──────────────────────────────────────────────────────────
with tab1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Top Team", filtered_matches['winner'].value_counts().idxmax())
    m2.metric("Total Runs", f"{filtered_deliveries['total_runs'].sum():,}")
    m3.metric("Total Wickets", len(filtered_deliveries[filtered_deliveries['dismissal_kind'].notna()]))
    m4.metric("Avg Match Score", int(filtered_deliveries.groupby('match_id')['total_runs'].sum().mean()))

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        st.subheader("🏆 Team Leaderboard")
        team_wins = filtered_matches['winner'].value_counts().reset_index()
        team_wins.columns = ['team', 'wins']
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=team_wins, x='wins', y='team', palette='Blues_r', ax=ax)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        st.subheader("🪙 Toss Impact")
        filtered_matches['toss_won_match'] = filtered_matches['toss_winner'] == filtered_matches['winner']
        toss_impact = filtered_matches['toss_won_match'].value_counts()
        fig, ax = plt.subplots(figsize=(5, 5.5))
        ax.pie(toss_impact, labels=['Lost Toss\nWon Match', 'Won Toss\nWon Match'], autopct='%1.1f%%', colors=['#FFD700', '#0052CC'], startangle=140, textprops={'color':"w", 'weight':'bold'})
        plt.tight_layout(); st.pyplot(fig); plt.close()

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🏏 Orange Cap Leaders")
        top_b = filtered_deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_b.values, y=top_b.index, palette='YlOrBr_r', ax=ax)
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with c4:
        st.subheader("🎳 Purple Cap Leaders")
        wickets = filtered_deliveries[filtered_deliveries['dismissal_kind'].notna() & ~filtered_deliveries['dismissal_kind'].isin(['run out','retired hurt','obstructing the field'])]
        top_bow = wickets.groupby('bowler')['dismissal_kind'].count().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_bow.values, y=top_bow.index, palette='Purples_r', ax=ax)
        plt.tight_layout(); st.pyplot(fig); plt.close()

# ──────────────────────────────────────────────────────────
# TAB 2: TEAM VS TEAM TOOL
# ──────────────────────────────────────────────────────────
with tab2:
    st.subheader("⚔️ Rivalry Analysis")
    all_teams = sorted(filtered_matches['team1'].unique())
    
    col_t1, col_t2 = st.columns(2)
    teamA = col_t1.selectbox("Select Team 1", all_teams, index=0)
    teamB = col_t2.selectbox("Select Team 2", all_teams, index=min(1, len(all_teams)-1))
    
    if teamA == teamB:
        st.error("Please select two different teams for comparison.")
    else:
        # Filter head-to-head matches
        h2h_matches = filtered_matches[
            ((filtered_matches['team1'] == teamA) & (filtered_matches['team2'] == teamB)) |
            ((filtered_matches['team1'] == teamB) & (filtered_matches['team2'] == teamA))
        ]
        
        if h2h_matches.empty:
            st.info(f"No matches found between {teamA} and {teamB} in the selected seasons.")
        else:
            # Stats calculation
            total_h2h = len(h2h_matches)
            winsA = len(h2h_matches[h2h_matches['winner'] == teamA])
            winsB = len(h2h_matches[h2h_matches['winner'] == teamB])
            
            # KPI Row
            k1, k2, k3 = st.columns(3)
            k1.metric(f"{teamA} Wins", winsA)
            k2.metric("Total Face-offs", total_h2h)
            k3.metric(f"{teamB} Wins", winsB)
            
            # Performance in these matches
            h2h_ids = h2h_matches['id'].tolist()
            h2h_deliveries = filtered_deliveries[filtered_deliveries['match_id'].isin(h2h_ids)]
            
            st.markdown("---")
            row_viz1, row_viz2 = st.columns([1, 1.5])
            
            with row_viz1:
                st.markdown("#### Win Distribution")
                fig, ax = plt.subplots()
                ax.pie([winsA, winsB], labels=[teamA, teamB], autopct='%1.1f%%', colors=['#FFD700', '#0052CC'], startangle=140, textprops={'color':"w"})
                st.pyplot(fig); plt.close()
                
            with row_viz2:
                st.markdown(f"#### Rivalry Top Performers")
                try:
                    # Top Scorer in these specific matches
                    top_h2h_batter = h2h_deliveries.groupby('batter')['batsman_runs'].sum().idxmax()
                    top_h2h_runs = h2h_deliveries.groupby('batter')['batsman_runs'].sum().max()
                    
                    # Top Wicket taker in these specific matches
                    h2h_wickets = h2h_deliveries[h2h_deliveries['dismissal_kind'].notna() & ~h2h_deliveries['dismissal_kind'].isin(['run out','retired hurt','obstructing the field'])]
                    top_h2h_bowler = h2h_wickets.groupby('bowler')['dismissal_kind'].count().idxmax()
                    top_h2h_wkts = h2h_wickets.groupby('bowler')['dismissal_kind'].count().max()
                    
                    st.info(f"🔥 **Top Scorer in this Rivalry:** {top_h2h_batter} ({int(top_h2h_runs)} runs)")
                    st.info(f"🎯 **Top Wicket Taker in this Rivalry:** {top_h2h_bowler} ({int(top_h2h_wkts)} wickets)")
                except:
                    st.info("Insufficient detail data for some head-to-head metrics in these seasons.")

# ──────────────────────────────────────────────────────────
# TAB 3: PLAYER SPOTLIGHT
# ──────────────────────────────────────────────────────────
with tab3:
    all_players = sorted(set(filtered_deliveries['batter'].dropna().tolist() + filtered_deliveries['bowler'].dropna().tolist()))
    selected_player = st.selectbox("Search for an IPL Player", options=[""] + all_players, index=0, placeholder="e.g. MS Dhoni")

    if selected_player:
        # Batting
        bat_p = filtered_deliveries[filtered_deliveries['batter'] == selected_player].copy()
        if not bat_p.empty:
            st.markdown(f"### 🏏 Batting — {selected_player}")
            tr = bat_p['batsman_runs'].sum()
            mp = bat_p['match_id'].nunique()
            out = filtered_deliveries[filtered_deliveries['player_dismissed'] == selected_player].shape[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Runs", tr); c2.metric("Matches", mp); c3.metric("Avg", round(tr/out, 2) if out > 0 else "∞")
            
            fig, ax = plt.subplots(figsize=(12, 3))
            bat_p['season'] = bat_p['match_id'].map(filtered_matches.set_index('id')['season'])
            sns.barplot(data=bat_p.groupby('season')['batsman_runs'].sum().reset_index(), x='season', y='batsman_runs', color='#FFD700', ax=ax)
            plt.tight_layout(); st.pyplot(fig); plt.close()

        # Bowling
        bow_p = filtered_deliveries[filtered_deliveries['bowler'] == selected_player].copy()
        if not bow_p.empty:
            st.markdown(f"### 🎳 Bowling — {selected_player}")
            wk_p = bow_p[bow_p['dismissal_kind'].notna() & ~bow_p['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])]
            c1, c2 = st.columns(2)
            c1.metric("Wickets", len(wk_p))
            balls_bowled = len(bow_p[bow_p['extras_type']!='wides'])
            c2.metric("Economy", round((bow_p['total_runs'].sum() / balls_bowled)*6, 2) if balls_bowled > 0 else 0)