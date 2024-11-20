import streamlit as st
import streamlit_analytics
from PIL import Image
from .utils import get_chatbot_config
from PIL import Image
from pathlib import Path

chatbot_config = get_chatbot_config() 

@st.dialog("Impressum")
def show_impressum():
    """
    Displays the Impressum content in a dialog box by loading 
    and rendering markdown from a file.
    """
    # Display logos side by side
    # col1, col2 = st.columns(2)
    # with col1:
    #     img1_path = get_image_path("eth_logo.png")
    #     img1 = Image.open(img1_path).resize((150, 35))
    #     st.image(img1)
    # with col2:
    #     img2_path = get_image_path("nccr_logo.png")
    #     img2 = Image.open(img2_path).resize((150, 35))
    #     st.image(img2)

    if st.session_state.lang == "de":
        file_path = Path(__file__).parent / "impressum_chatbot_de.md"
    else: 
        file_path = Path(__file__).parent / "impressum_chatbot_en.md"

    with open(file_path, "r") as file:
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
    # Define a container for the footer
    disclaimer_placeholder = st.container()

    with disclaimer_placeholder:
        col1, col2 = st.columns([0.3, 0.7],vertical_alignment="top")  # Two columns for alignment

        # Right column: Impressum button
        with col1:
            # CSS styling for button
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
                    font-size: 13px;
                    text-decoration: underline;
                    cursor: pointer;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Invisible span to target the button
            st.markdown('<span id="button-after"> </span>', unsafe_allow_html=True)

            # Visible Impressum button
            current_version = chatbot_config["version"]

            if st.button("V" + current_version + ", Impressum"):
                show_impressum()


        
