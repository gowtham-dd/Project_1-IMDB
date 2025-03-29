import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import re  

# ✅ Convert "53K" → 53000, "1.2M" → 1200000
def convert_votes(value):
    if isinstance(value, str):
        value = value.lower().replace(",", "")  # Remove commas
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

if df.empty:
    st.error("❌ No data available. Please check the database connection.")
else:
    st.title("🎬 IMDb Movie Explorer")

    st.sidebar.header("🔍 Search for a Movie")
    movie_list = [""] + df["title"].unique().tolist()
    selected_movie = st.sidebar.selectbox("Select movie...", movie_list)

    st.sidebar.header("🔧 Filters")

    if selected_movie:
        searched_df = df[df["title"] == selected_movie]  
    else:
        searched_df = df.copy()

        if not selected_movie:
            duration_filter = st.sidebar.radio("⏳ Duration (Hrs)", ["All", "< 2 Hrs", "2-3 Hrs", "> 3 Hrs"])
            if duration_filter == "< 2 Hrs":
                searched_df = searched_df[searched_df["duration"] < 2.0]
            elif duration_filter == "2-3 Hrs":
                searched_df = searched_df[(searched_df["duration"] >= 2.0) & (searched_df["duration"] <= 3.0)]
            elif duration_filter == "> 3 Hrs":
                searched_df = searched_df[searched_df["duration"] > 3.0]

        if not selected_movie:
            min_rating = st.sidebar.slider("⭐ Minimum IMDb Rating", 0.0, 10.0, 8.0, 0.1)
            searched_df = searched_df[searched_df["rating"] >= min_rating]

        if not selected_movie and not searched_df.empty:
            min_votes = st.sidebar.slider("🔢 Minimum Votes", int(searched_df["voting"].min()), int(searched_df["voting"].max()), 5000)
            searched_df = searched_df[searched_df["voting"] >= min_votes]

        if not selected_movie and "genre" in searched_df.columns and not searched_df.empty:
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

        # ✅ **Updated Pie Chart Based on Filtered Genre**
        genre_filtered_counts = searched_df["genre"].value_counts().reset_index()
        genre_filtered_counts.columns = ["Genre", "Count"]

        if not genre_filtered_counts.empty:
            fig_genre_pie = px.pie(genre_filtered_counts, names="Genre", values="Count", title="🎭 Genre Distribution in Filtered Results")
            st.plotly_chart(fig_genre_pie, use_container_width=True)

        fig_votes = px.scatter(searched_df, x="voting", y="rating", size="voting", title="🔢 Votes vs Ratings", color="rating", hover_name="title")
        st.plotly_chart(fig_votes, use_container_width=True)

    else:
        st.warning("⚠️ No movies match the selected filters. Try adjusting them.")
