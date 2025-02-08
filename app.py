import os
import streamlit as st
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
import requests
import pandas as pd
import plotly.express as px

# Load environment variables
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# NASA_API_KEY = os.getenv("NASA_API_KEY")
# For deployment on streamlit 
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NASA_API_KEY = st.secrets["NASA_API_KEY"]
# Ensure API keys are provided
if not GROQ_API_KEY or not NASA_API_KEY:
    st.error("API keys are missing! Add them to the .env file.")
    st.stop()

# Define State
class State(TypedDict):
    messages: Annotated[List[dict], "messages"]

# Initialize LLM with Groq
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

# Function to fetch NASA data
def fetch_nasa_data():
    try:
        endpoint = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {"api_key": NASA_API_KEY}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Function to visualize NASA data
def visualize_data(data):
    if "near_earth_objects" in data:
        asteroids = [
            {
                "name": obj["name"],
                "diameter": obj["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
            }
            for date in data["near_earth_objects"]
            for obj in data["near_earth_objects"][date]
        ]
        if asteroids:
            df = pd.DataFrame(asteroids)
            fig = px.bar(df, x="name", y="diameter", title="Asteroid Diameters", labels={"diameter": "Diameter (km)"})
            st.plotly_chart(fig)
        else:
            st.write("No asteroids found for visualization.")
    else:
        st.write("No data available.")

# Chatbot Function
def chatbot(state: State):
    user_message = state["messages"][-1]["content"]  # Get the latest user message
    ai_response = llm.invoke(user_message)  # Generate AI response
    return {"messages": state["messages"] + [{"role": "assistant", "content": ai_response.content}]}

# NASA Data Node
def nasa_data_node(state: State):
    data = fetch_nasa_data()
    return {"messages": state["messages"] + [{"role": "nasa_data", "content": data}]}

# Build LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("nasa_data", nasa_data_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "nasa_data")
graph_builder.add_edge("nasa_data", END)

graph = graph_builder.compile()

# Streamlit UI
st.set_page_config(page_title="🚀 AI Space Data Explorer", layout="wide")
st.title("🚀 AI Space Data Explorer")
st.sidebar.header("🔍 Explore Space Data")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User Input
user_input = st.text_area("💬 Ask something about space:", height=100)

if st.button("Submit"):
    if user_input.strip() == "":
        st.error("Please enter a question!")
    else:
        with st.spinner("🚀 Thinking..."):
            # Prepare initial state
            initial_state = {"messages": [{"role": "user", "content": user_input}]}
            
            # Stream the graph
            try:
                for event in graph.stream(initial_state, stream_mode="values"):
                    response = event["messages"][-1]  # Get latest response
                    st.session_state.chat_history.append(response)  # Save to history
                    
                    if response["role"] == "assistant":
                        st.subheader("🤖 AI Response:")
                        st.write(response["content"])
                    
                    if response["role"] == "nasa_data":
                        st.subheader("📊 NASA Data Visualization:")
                        visualize_data(response["content"])
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display Chat History
st.sidebar.subheader("📜 Chat History")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.sidebar.markdown(f"🧑 **You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.sidebar.markdown(f"🤖 **AI:** {msg['content']}")

# About Section
st.sidebar.subheader("🌍 About")
st.sidebar.write("This application provides real-time AI-powered insights into space data using NASA APIs and LangGraph-based multi-agent AI.")
st.sidebar.write("💡 Built with LangGraph, Streamlit, and Plotly.")