# 🎬 IMDb Movie Explorer  

An interactive **Streamlit-based IMDb Movie Explorer** that enables users to **search, filter, and analyze** movie data from a **MySQL database**. This intuitive dashboard provides **real-time insights** into IMDb movie statistics, offering a seamless user experience with **dynamic visualizations**.

---

## 🚀 Features  
✔️ **Advanced Search & Filters** – Search by title or filter movies based on **duration, IMDb rating, votes, and genre**  
✔️ **Exact Duration Conversion** – Displays duration in **decimal format** (e.g., `2h 3m` → `2.05 hours`)  
✔️ **Accurate Voting Conversion** – Converts `53K` into `53000` for precise filtering  
✔️ **Interactive Visualizations** – Dynamic **bar, pie, and scatter plots** for better analysis  
✔️ **Filtered Genre Insights** – Pie chart highlights **top genres** based on selected filters  
✔️ **MySQL Integration** – Fetches **real-time movie data** from a structured **database**  

---

## 🖥️ Dashboard Preview  
![Dashboard](images/dashboard.png)  

> ⚡ *Ensure the `images/` folder contains your dashboard screenshot*  

---

## 📂 Project Structure  
```bash
📁 IMDb Movie Explorer
│── 📄 main.py               # Streamlit application
│── 📄 README.md             # Project documentation
│── 📄 requirements.txt      # Dependencies list
│── 📁 images/               # Folder for screenshots
```

---

## 🛠 Installation & Setup  
### 🔹 Step 1: Clone the Repository  
```sh
git clone https://github.com/gowtham-dd/Project_1-IMDB.git
cd Project_1-IMDB
```

### 🔹 Step 2: Install Dependencies  
```sh
pip install -r requirements.txt
```

### 🔹 Step 3: Run the Application  
```sh
streamlit run main.py
```

---

## 🔧 Technology Stack  
- **Python** (Pandas, MySQL Connector, Plotly)  
- **Streamlit** (Interactive UI)  
- **MySQL** (Database for movie records)  
- **Git & GitHub** (Version control and collaboration)  

---

## 🤝 Contributing  
We welcome contributions! Feel free to **fork the repository, raise issues, or submit pull requests** to enhance this project.

---

## 📜 License  
This project is licensed under the **MIT License**.

