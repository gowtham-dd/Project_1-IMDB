import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import re  

# ✅ Page Navigation
st.sidebar.title("🎬 IMDb Dashboard")
page = st.sidebar.radio("Go to", ["Movie Explorer", "Advanced Insights"])

st.markdown("""
    <style>
        /* Background color */
        .stApp {
            background-color: #1D3557;
        }

        /* Sidebar design */
        .css-1d391kg {
            background-color: #457B9D !important;
        }

        /* Change text color */
        h1, h2, h3, h4, h5, h6, p, .stTextInput, .stSelectbox {
            color: #F1FAEE !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #E63946 !important;
            color: white !important;
            border-radius: 10px !important;
        }

        /* Dataframe styling */
        .dataframe {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)


# ✅ Convert "53K" → 53000, "1.2M" → 1200000
def convert_votes(value):
    if isinstance(value, str):
        value = value.lower().replace(",", "")  
        if "k" in value:
            return int(float(value.replace("k", "")) * 1000)
        elif "m" in value:
            return int(float(value.replace("m", "")) * 1000000)
    try:
        return int(value)
    except ValueError:
        return 0  


# ✅ Convert "2h 3m" → 2.05 Hours
def convert_duration(duration):
    if isinstance(duration, str):
        duration = duration.lower().replace("hrs", "h").replace("hr", "h").replace("mins", "m").replace("min", "m")
        hours_match = re.search(r"(\d+)h", duration)
        minutes_match = re.search(r"(\d+)m", duration)
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        return round(hours + (minutes / 60), 2)  
    return 0  


# ✅ Fetch Movie Data
def get_movie_data():
    try:
        connection = mysql.connector.connect(
            host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port=4000,
            user="4PFhDQQc2yhfCUH.root",
            password="tzNB9UAMnXNidi62",
            database="movies_database",
        )
        
        query = "SELECT * FROM movies"
        df = pd.read_sql(query, connection)
        connection.close()

        df.rename(columns=lambda x: x.strip().lower(), inplace=True)

        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        
        if 'duration' in df.columns:
            df["duration"] = df["duration"].astype(str).map(convert_duration)
        
        if 'voting' in df.columns:
            df["voting"] = df["voting"].astype(str).map(convert_votes)
            df["voting"] = pd.to_numeric(df["voting"], errors="coerce").fillna(0).astype(int)

        return df

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return pd.DataFrame()  

df = get_movie_data()


# ✅ PAGE 1: MOVIE EXPLORER
if page == "Movie Explorer":
    st.markdown("<h1 style='text-align: center; color: #F1FAEE;'>🎬 IMDb Movie Explorer</h1>", unsafe_allow_html=True)

    if df.empty:
        st.error("❌ No data available. Please check the database connection.")
    else:
        st.sidebar.header("🔍 Search for a Movie")
        movie_list = [""] + df["title"].unique().tolist()
        selected_movie = st.sidebar.selectbox("Select movie...", movie_list)

        st.sidebar.header("🔧 Filters")

        if selected_movie:
            searched_df = df[df["title"] == selected_movie]  
        else:
            searched_df = df.copy()

            duration_filter = st.sidebar.radio("⏳ Duration (Hrs)", ["All", "< 2 Hrs", "2-3 Hrs", "> 3 Hrs"])
            if duration_filter == "< 2 Hrs":
                searched_df = searched_df[searched_df["duration"] < 2.0]
            elif duration_filter == "2-3 Hrs":
                searched_df = searched_df[(searched_df["duration"] >= 2.0) & (searched_df["duration"] <= 3.0)]
            elif duration_filter == "> 3 Hrs":
                searched_df = searched_df[searched_df["duration"] > 3.0]

            min_rating = st.sidebar.slider("⭐ Minimum IMDb Rating", 0.0, 10.0, 8.0, 0.1)
            searched_df = searched_df[searched_df["rating"] >= min_rating]

            min_votes = st.sidebar.slider("🔢 Minimum Votes", int(searched_df["voting"].min()), int(searched_df["voting"].max()), 5000)
            searched_df = searched_df[searched_df["voting"] >= min_votes]

            genres = searched_df["genre"].unique()
            selected_genre = st.sidebar.multiselect("🎭 Select Genre(s)", genres, default=genres)
            searched_df = searched_df[searched_df["genre"].isin(selected_genre)]

        st.write(f"### Filtered Movies ({len(searched_df)} results)")
        st.dataframe(searched_df)

# ✅ PAGE 2: ADVANCED INSIGHTS
elif page == "Advanced Insights":
    st.markdown("<h1 style='text-align: center; color: #F1FAEE;'>📊 Advanced Movie Insights</h1>", unsafe_allow_html=True)

    if df.empty:
        st.error("❌ No data available.")
    else:
        st.subheader("🏆 Top 10 Movies by Rating & Votes")
        top_movies = df.sort_values(["rating", "voting"], ascending=[False, False]).head(10)
        st.dataframe(top_movies)

        st.subheader("🎭 Genre Distribution")
        genre_counts = df["genre"].value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]
        fig_genre = px.bar(genre_counts, x="Genre", y="Count", color="Genre", title="Movies per Genre")
        st.plotly_chart(fig_genre, use_container_width=True)

        st.subheader("⏳ Average Duration by Genre")
        avg_duration = df.groupby("genre")["duration"].mean().reset_index()
        fig_duration = px.bar(avg_duration, x="duration", y="genre", orientation="h", title="Average Duration by Genre")
        st.plotly_chart(fig_duration, use_container_width=True)

        st.subheader("🔢 Voting Trends by Genre")
        avg_votes = df.groupby("genre")["voting"].mean().reset_index()
        fig_votes = px.bar(avg_votes, x="genre", y="voting", title="Average Voting by Genre", color="voting")
        st.plotly_chart(fig_votes, use_container_width=True)

        st.subheader("📊 Correlation: Ratings vs Votes")
        fig_corr = px.scatter(df, x="voting", y="rating", title="Ratings vs Voting", color="rating", hover_name="title")
        st.plotly_chart(fig_corr, use_container_width=True)
