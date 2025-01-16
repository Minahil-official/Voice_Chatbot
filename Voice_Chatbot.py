from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

# Access API keyss
weather_api_key = os.getenv("weather_api_key")
google_key = os.getenv("GOOGLE_API_KEY")
news_key = os.getenv("News_api_key")


import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
import speech_recognition as sr
from gtts import gTTS
import tempfile
import playsound


# Function: Text-to-Speech (Output Audio)
def handle_audio_input():
    recognizer = sr.Recognizer()
    
    # Listen for audio input
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        audio = recognizer.listen(source)
    
    try:
        text_input = recognizer.recognize_google(audio)
        st.success(f"Your text: {text_input}")
        
        # Simulate AI response (replace with actual LLM logic)
        with st.spinner("AI Responding..."):
            response = llm.invoke(text_input)  
            response = str(response.content)  
            
            if response:
                # Generate and play audio response
                tts = gTTS(text=response, lang='en' ,tld='com')
                audio_file = "response.mp3"
                tts.save(audio_file)
                
                # Display audio for playback
                st.audio(audio_file, format="audio/mp3")
                
                # Optionally clean up the generated file
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand that.")
    except sr.RequestError:
        st.error("Sorry, the speech recognition service is unavailable.")



# Function: Speech-to-Text (Input Audio)
def listen():
    """
    Listens to the user's speech and converts it to text using Google Speech Recognition.
    Returns:
        str: The recognized text from speech.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"


# Define a Calculator Tool
@tool
def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression and returns the result.
    """
    import math
    allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
    allowed_names.update({"abs": abs, "round": round})
    try:
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: Invalid expression. Details: {e}"


# Define a Weather Tool
@tool
def fetch_weather(city: str) -> str:
    """
    Fetches weather information for a given city.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": weather_api_key,
        "units": "metric",
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'Unknown error occurred.')}"
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        city_name = data["name"]
        return (
            f"Weather in {city_name}:\n"
            f"- Description: {weather}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Humidity: {humidity}%"
        )
    except Exception as e:
        return f"Error: Unable to fetch weather data. Details: {e}"
    
    
@tool
# Function to fetch the latest news
def fetch_latest_news(query: str = "latest", language: str = "en", page_size: int = 5):
    """
    Fetches the latest news articles based on a query.

    Parameters:
    - query (str): The keyword for the news search (default is 'latest').
    - language (str): Language for the news (default is 'en').
    - page_size (int): Number of news articles to fetch (default is 5).

    Returns:
    - list: A list of dictionaries with news headlines, descriptions, and URLs.
    """
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": news_key,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        articles = response.json().get("articles", [])

        news = []
        for article in articles:
            news.append({
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
            })

        return news
    except Exception as e:
        return {"error": str(e)}


# LangChain Agent Setup
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=google_key)
tools = [calculator, fetch_weather,fetch_latest_news]
agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION)

# Streamlit App UI
st.title("Multimodal Chatbot with Audio")
st.sidebar.write("Available Tools:")
st.sidebar.write("- Calculator")
st.sidebar.write("- Weather")
st.sidebar.write("- Fetch Latest News")





user_input = st.text_input("Enter your query")
if st.button("Submit"):
    response = agent.invoke(user_input)
    st.write(response)
        # Speak the response


# Streamlit App
if st.button("Start Speaking"):
    with st.spinner("Listening..."):
        handle_audio_input()



