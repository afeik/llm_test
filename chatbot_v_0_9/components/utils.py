import time
import streamlit as st
import json
import base64

def get_chatbot_config():
    """
    Loads and returns the chatbot configuration from a JSON file.
    """
    with open("./components/chatbot_config_v_0_9.json", "r") as config_file:
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
