import streamlit as st
from PIL import Image
from .utils import get_chatbot_config, get_image_path
import os 
from PIL import Image

chatbot_config = get_chatbot_config() 

@st.dialog("Impressum")
def show_impressum():
    """
    Displays the Impressum content in a dialog box by loading 
    and rendering markdown from a file.
    """
    with open("components/impressum_chatbot.md", "r") as file:
        markdown_content = file.read()
    st.markdown(markdown_content)


def write_footnote(short_version=False): 
    """
    Displays a footer with a disclaimer and version information,
    along with an Impressum button and partner logos.
    
    Parameters:
    -----------
    short_version : bool, optional
        If True, displays a simplified version of the disclaimer.
    """
    disclaimer_placeholder = st.container(border=None)
    
    with disclaimer_placeholder:
        if not short_version: 
            disclaimer = chatbot_config["disclaimer"]
            st.markdown(
                f"""
                <div style='color: gray; font-size: 13px;'>
                    {disclaimer}
                </div>
                """,
                unsafe_allow_html=True
            )  
        
        # CSS styling for elements in the footnote
        st.markdown(
            """
            <style>
            /* Hide specific elements */
            .element-container:has(style) {
                display: none;
            }
            #button-after {
                display: none;
            }
            .element-container:has(#button-after) {
                display: none;
            }
            
            /* Style the button with a smaller font size */
            .element-container:has(#button-after) + div button {
                background-color: transparent;
                color: gray;
                border: none;
                padding: 0;
                text-decoration: underline;
                cursor: pointer;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"<p style='font-size:0.8em !important;'>", unsafe_allow_html=True)

        # Invisible span to target the button
        st.markdown('<span id="button-after"> </span>', unsafe_allow_html=True)

        # Button for Impressum, showing the current chatbot version
        current_version = chatbot_config["version"]
        if st.button("Version " + current_version + ", Impressum"):
            show_impressum()
        st.markdown(f"</p>", unsafe_allow_html=True)

        # Display logos side by side
        col1, col2 = st.columns(2)
        with col1:
            img1_path = get_image_path("eth_logo.png")
            img1 = Image.open(img1_path).resize((150, 35))
            st.image(img1)
        with col2:
            img2_path = get_image_path("eth_logo.png")
            img2 = Image.open(img2_path).resize((150, 35))
            st.image(img2)
