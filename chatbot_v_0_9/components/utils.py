import time
import streamlit as st
import json
import base64
import os
from pathlib import Path
import gettext

# Function to get the absolute path to the image
def get_image_path(image_name):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "images", image_name)

def get_chatbot_config():
    """
    Loads and returns the chatbot configuration from a JSON file.
    """
    # Define the absolute path to the JSON file
    file_path = Path(__file__).parent / "chatbot_config_v_0_9.json"

    # Load the configuration
    with open(file_path, "r") as config_file:
        return json.load(config_file)

def stream_data(text):
    """
    Yields each word in the given text with a brief pause for streaming effect.
    """
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

@st.cache_resource()
def get_base64_of_bin_file(bin_file):
    """
    Reads a binary file, encodes it in base64, and returns the encoded string.
    """
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def set_png_as_page_bg(png_file):
    """
    Sets the given PNG file as the background image of the Streamlit app.
    """
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    body {{
    background-image: url("data:image/png;base64,{bin_str}");
    background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def set_background_color(color):
    """
    Sets a solid background color for the Streamlit app.
    
    Parameters:
    color (str): The background color as a CSS color string (e.g., "#90CAF9" or "blue").
    """
    st.markdown(f"<style>.stApp {{background-color: {color};}}</style>", unsafe_allow_html=True)

def set_background_local(image_file):
    """
    Sets a local image file as the background of the Streamlit app.

    Parameters:
    image_file (str): Path to the image file to use as the background.
    """
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def language_dropdown(ret_cols=False): 
    # Directory for language files
    
    locale_dir = st.session_state.locale_dir

    # Map language codes to display names
    languages = {
        "de": "DE 🇩🇪",
        "en": "EN 🇬🇧",
    }

    # Streamlit Layout: Use columns to place the dropdown on the right
    if ret_cols is False:
        col1, col2, col3 = st.columns([6,3,1.8])  # Adjust column ratios for layout control

        with col3:
            selected_language = st.selectbox(" ", list(languages.values()), label_visibility="collapsed")
    else:
        col1, col2, col3 = st.columns([6,1.8,3])
        with col2: 
            selected_language = st.selectbox(" ", list(languages.values()), label_visibility="collapsed")
    
    # Get the corresponding locale code
    current_lang = [code for code, name in languages.items() if name == selected_language][0]

    # Store selected language in session state
    st.session_state.lang = current_lang

    # Load the corresponding translation
    lang = gettext.translation("messages", localedir=locale_dir, languages=[current_lang], fallback=True)
    lang.install()
    _ = lang.gettext

    if ret_cols:
        return _, col3
    else: 
        return _
    