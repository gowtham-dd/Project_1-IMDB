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

df.rename(columns=lambda x: x.strip().lower(), inplace=True)

if 'rating' in df.columns:
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        
if 'duration' in df.columns:
    df["duration"] = df["duration"].astype(str).map(convert_duration)
        
if 'voting' in df.columns:
    df["voting"] = df["voting"].astype(str).map(convert_votes)
    df["voting"] = pd.to_numeric(df["voting"], errors="coerce").fillna(0).astype(int)

  

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
        if not searched_df.empty:
           st.subheader("📊 Movie Insights")

        if "genre" in searched_df.columns:
            genre_counts = searched_df["genre"].value_counts().reset_index()
            genre_counts.columns = ["Genre", "Count"]
            fig_genre = px.bar(genre_counts, x="Genre", y="Count", title="🎭 Movies per Genre", color="Genre")
            st.plotly_chart(fig_genre, use_container_width=True)

        fig_ratings = px.histogram(searched_df, x="rating", nbins=20, title="⭐ IMDb Ratings Distribution", color_discrete_sequence=["#FF5733"])
        st.plotly_chart(fig_ratings, use_container_width=True)

        genre_filtered_counts = searched_df["genre"].value_counts().reset_index()
        genre_filtered_counts.columns = ["Genre", "Count"]
        if not genre_filtered_counts.empty:
            fig_genre_pie = px.pie(genre_filtered_counts, names="Genre", values="Count", title="🎭 Genre Distribution in Filtered Results")
            st.plotly_chart(fig_genre_pie, use_container_width=True)

        fig_votes = px.scatter(searched_df, x="voting", y="rating", size="voting", title="🔢 Votes vs Ratings", color="rating", hover_name="title")
        st.plotly_chart(fig_votes, use_container_width=True)

        # ✅ Voting Percentage Pie Chart
        vote_bins = [0, 5000, 20000, 50000, 100000, searched_df['voting'].max()]
        vote_labels = ["<5K", "5K-20K", "20K-50K", "50K-100K", "100K+"]
        searched_df["vote_category"] = pd.cut(searched_df["voting"], bins=vote_bins, labels=vote_labels)
        vote_counts = searched_df["vote_category"].value_counts().reset_index()
        vote_counts.columns = ["Vote Range", "Count"]
        fig_vote_pie = px.pie(vote_counts, names="Vote Range", values="Count", title="🔢 Voting Distribution")
        st.plotly_chart(fig_vote_pie, use_container_width=True)

        # ✅ Average Rating per Genre
        avg_rating_genre = searched_df.groupby("genre")["rating"].mean().reset_index()
        fig_avg_rating = px.bar(avg_rating_genre, x="genre", y="rating", title="⭐ Average Rating per Genre", color="rating")
        st.plotly_chart(fig_avg_rating, use_container_width=True)

        # ✅ Movie Duration Distribution
        fig_duration = px.histogram(searched_df, x="duration", title="⏳ Movie Duration Distribution")
        st.plotly_chart(fig_duration, use_container_width=True)

        # ✅ Yearly Movie Release Trend
        if "year" in searched_df.columns:
            yearly_counts = searched_df["year"].value_counts().reset_index()
            yearly_counts.columns = ["Year", "Count"]
            fig_year_trend = px.line(yearly_counts, x="Year", y="Count", title="📅 Yearly Movie Release Trend")
            st.plotly_chart(fig_year_trend, use_container_width=True)

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

        st.subheader("⭐ Rating Distribution")
        fig_rating_dist = px.histogram(df, x="rating", nbins=20, title="IMDb Ratings Distribution", color_discrete_sequence=["#FF5733"])
        st.plotly_chart(fig_rating_dist, use_container_width=True)

        st.subheader("🎭 Genre-Based Rating Leaders")
        genre_top_movies = df.loc[df.groupby("genre")["rating"].idxmax()][["genre", "title", "rating"]]
        st.dataframe(genre_top_movies)

        st.subheader("🔢 Most Popular Genres by Voting")
        genre_vote_counts = df.groupby("genre")["voting"].sum().reset_index()
        fig_popular_genres = px.pie(genre_vote_counts, names="genre", values="voting", title="Most Popular Genres by Total Votes")
        st.plotly_chart(fig_popular_genres, use_container_width=True)

        st.subheader("⏳ Duration Extremes")
        shortest_movie = df.loc[df["duration"].idxmin()][["title", "duration"]]
        longest_movie = df.loc[df["duration"].idxmax()][["title", "duration"]]
        st.write(f"**Shortest Movie:** {shortest_movie['title']} ({shortest_movie['duration']} hrs)")
        st.write(f"**Longest Movie:** {longest_movie['title']} ({longest_movie['duration']} hrs)")

        st.subheader("🔥 Ratings by Genre (Heatmap)")
        avg_ratings_heatmap = df.pivot_table(index="genre", values="rating", aggfunc="mean")
        fig_heatmap = px.imshow(avg_ratings_heatmap, color_continuous_scale="reds", title="Average Ratings by Genre")
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("📊 Correlation: Ratings vs Votes")
        fig_corr = px.scatter(df, x="voting", y="rating", title="Ratings vs Voting", color="rating", hover_name="title")
        st.plotly_chart(fig_corr, use_container_width=True)