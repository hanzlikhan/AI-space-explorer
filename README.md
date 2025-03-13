# AI-space-explorer
# 🚀 AI Space Data Explorer

An AI-powered web app that provides real-time space data insights using **NASA APIs** and **Groq AI models**. Built with **LangGraph, Streamlit, and Plotly**.

## 🌟 Features
- 🤖 AI chatbot powered by **Groq's Llama-3.3-70B** model.
- 📊 Fetches and visualizes **near-Earth asteroids** using **NASA's API**.
- 🗂️ Interactive **chat history** for better user experience.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Integration:** LangGraph, Groq API (Llama-3.3-70B)
- **Data Processing:** Pandas, NASA APIs
- **Visualization:** Plotly

---

## 🚀  Installation & Setup

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/your-username/AI-Space-Data-Explorer.git
cd AI-Space-Data-Explorer
```
## Make a Virtual environment for install libraries 
``` sh
pip install virtualenv
virtualenv myenv
myenv\Scripts\activate
```
### **2️⃣ Install Dependencies**

```sh
pip install -r requirements.txt
```

### **3️⃣ Set up API Keys**

- Create a .streamlit folder and add a file secrets.toml and then add your NASA API key and Groq API key in the following format:
- Replace `YOUR_NASA_API_KEY` and `YOUR_GROQ_API_KEY` with your

```sh
NASA_API_KEY=YOUR_NASA_API_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

## Running App 

``` sh
streamlit run app.py
```

Open your web browser and navigate to `http://localhost:8501` to access the app.

## Deployment on Streamlit Cloud

1. Push this project to GitHub.
2. Go to Streamlit Cloud and create a new app.
3. Select your repository and deploy.
4. Add API keys in Streamlit Secrets.

## 🤝 Contributing

- Want to improve this project? Feel free to fork and submit PRs!

## 📜 License
- MIT License © 2025 Muhammad Hanzla
