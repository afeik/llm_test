import streamlit as st
from .footnote import write_footnote
from .db_communication import update_proficiency, init_db_communication
from .utils import get_image_path, language_dropdown, get_chatbot_config
from PIL import Image

chatbot_config = get_chatbot_config()

def select_proficiency_level():
    """
    Prompts the user to select their experience level with the energy transition.
    """
    _ = language_dropdown()
    lang = st.session_state.lang

    # Load titles and text from the configuration file
    page_title = chatbot_config["titles"]["front_page"][lang]["page_title"]
    slider_title = chatbot_config["titles"]["front_page"][lang]["slider_title"]
    consent_text = chatbot_config["titles"]["front_page"][lang]["consent_text"]

    # Initialize session state variables
    if "proficiency" not in st.session_state:
        st.session_state.proficiency = None
    if "proficiency_selected" not in st.session_state:
        st.session_state.proficiency_selected = False
    if "step" not in st.session_state:
        st.session_state.step = "select_proficiency"
    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    # Display the proficiency selection page
    st.markdown(f"<h3>{page_title}</h3>", unsafe_allow_html=True)

    # Load and display the image
    image_path = get_image_path("project_solarstories.jpg")
    image = Image.open(image_path)
    st.image(image, use_column_width=True)

    # Slider for proficiency rating
    st.session_state.proficiency_rating = st.slider(
        slider_title,
        0, 100,
        value=st.session_state.get("proficiency_rating", 0),
        key="proficiency_slider"
    )

    # Checkbox for consent
    st.session_state.consent_given = st.checkbox(
        consent_text,
        value=st.session_state.get("consent_given", False),
        key="consent_checkbox"
    )

    # Determine proficiency level
    if 0 <= st.session_state.proficiency_rating <= 33:
        st.session_state.proficiency = "beginner"
    elif 34 <= st.session_state.proficiency_rating <= 66:
        st.session_state.proficiency = "intermediate"
    elif 67 <= st.session_state.proficiency_rating <= 100:
        st.session_state.proficiency = "expert"

    # Start Chatbot button
    if st.button(_("Start Chatbot"), disabled=not st.session_state.consent_given, key="start_chatbot_button"):
        st.session_state.proficiency_selected = True
        st.session_state.step = "initial_statement"

        try:
            init_db_communication()
            update_proficiency()
        except Exception as e:
            st.error(f"An error occurred during initialization: {e}")

        st.rerun()

    # Footer
    write_footnote(short_version=True)
