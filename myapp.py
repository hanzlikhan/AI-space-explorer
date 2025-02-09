import os
import streamlit as st
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
import requests
import pandas as pd
import plotly.express as px
import uuid

# Load environment variables for deployment
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NASA_API_KEY = st.secrets["NASA_API_KEY"]

# Ensure API keys are provided
if not GROQ_API_KEY or not NASA_API_KEY:
    st.error("API keys are missing! Add them to the .env file.")
    st.stop()

# Define State
class State(TypedDict):
    messages: Annotated[List[dict], "accumulate"]

# Initialize LLM with Groq
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

# Function to fetch NASA data (only asteroid details)
def fetch_nasa_data():
    try:
        endpoint = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {"api_key": NASA_API_KEY}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Function to visualize NASA asteroid data (only graph)
def visualize_data(data):
    if "error" in data:
        st.error(f"Error fetching NASA data: {data['error']}")
        return
    
    if "near_earth_objects" in data:
        asteroids = []
        for date in data["near_earth_objects"]:
            for obj in data["near_earth_objects"][date]:
                asteroids.append({
                    "name": obj["name"],
                    "diameter": obj["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
                })
        
        if asteroids:
            df = pd.DataFrame(asteroids)
            fig = px.bar(df, x="name", y="diameter", title="Asteroid Diameters", labels={"diameter": "Diameter (km)"})

            unique_key = f"chart_{uuid.uuid4().hex}"  # Generate a unique key
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
        else:
            st.write("No asteroid data available.")
    else:
        st.write("No data available.")

# Chatbot Function
def chatbot(state: State):
    user_message = state["messages"][-1]["content"]
    ai_response = llm.invoke(user_message)  
    return {"messages": [{"role": "assistant", "content": ai_response.content}]} 

# NASA Data Node (Only visualization)
def nasa_data_node(state: State):
    data = fetch_nasa_data()
    return {"messages": [{"role": "nasa_data", "content": data}]} 

# Build LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("nasa_data", nasa_data_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "nasa_data")

graph = graph_builder.compile()

# Streamlit UI
st.set_page_config(page_title="🚀 AI Space Data Explorer", layout="wide")
st.title("🚀 AI Space Data Explorer")
st.sidebar.header("🔍 Explore Space Data")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chatbot UI
user_input = st.chat_input("💬 Ask something about space:")
if user_input:
    with st.spinner("🚀 Thinking..."):
        initial_state = {"messages": [{"role": "user", "content": user_input}]}

        final_event = None  # Store the final event from the stream

        try:
            for event in graph.stream(initial_state, stream_mode="values"):
                final_event = event  # Keep updating with the latest response

        except Exception as e:
            st.error(f"An error occurred: {e}")

        if final_event:
            response = final_event["messages"][-1]  # Get the last response

            # Display user message only once
            with st.chat_message("user"):
                st.write(user_input)

            st.session_state.chat_history.append(response)  # Store response in history

            # Handle different response types
            if response["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(response["content"])

            elif response["role"] == "nasa_data":
                with st.chat_message("assistant"):
                    st.subheader("📊 NASA Asteroid Data")
                    visualize_data(response["content"])

            elif response["role"] == "apod":
                with st.chat_message("assistant"):
                    st.subheader("🌌 Astronomy Picture of the Day")
                    visualize_apod(response["content"])
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display Chat History
for msg in st.session_state.chat_history:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        if role == "assistant" and "nasa_data" in msg["role"]:
            visualize_data(msg["content"])
        else:
            st.write(msg["content"])

# Sidebar About Section
st.sidebar.subheader("🌍 About")
st.sidebar.write("This application provides AI-powered insights into space using NASA APIs and LangGraph-based AI.")
st.sidebar.write("💡 Built with LangGraph, Streamlit, and Plotly.")
