import streamlit as st
from .footnote import write_footnote
from .db_communication import update_proficiency, init_db_communication
from .utils import get_image_path, language_dropdown
from PIL import Image

def select_proficiency_level():
    """
    Prompts the user to select their experience level with the energy transition.
    """
    _ = language_dropdown()  # Ensure _ is callable

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

    placeholder = st.empty()

    with placeholder.container():
        st.markdown(_("<h3>Welcome to the Energy Transition Chatbot!</h3>"), unsafe_allow_html=True)

        # Load and display the image

        image_path = get_image_path("energy_transition_switzerland.png")
        image = Image.open(image_path)
        st.image(image, use_column_width=True)

        # Slider for proficiency rating
        proficiency_rating = st.slider(
            _("How would you rate your knowledge about the energy transition?"), 0, 100
        )

        # Checkbox for consent
        consent_given = st.checkbox(
            _("I acknowledge that data collected during this session will be securely stored and used solely for research purposes at ETH Zurich.")
        )

        # Determine proficiency level
        if 0 <= proficiency_rating <= 33:
            st.session_state.proficiency = "beginner"
        elif 34 <= proficiency_rating <= 66:
            st.session_state.proficiency = "intermediate"
        elif 67 <= proficiency_rating <= 100:
            st.session_state.proficiency = "expert"

        # Start Chatbot button
        if st.button("Start Chatbot", disabled=not consent_given):
            st.session_state.proficiency_selected = True
            st.session_state.step = "initial_statement"
            st.session_state.consent_given = True
            placeholder.empty()
            try:
                init_db_communication()
                update_proficiency()
            except Exception as e:
                st.error(f"An error occurred during initialization: {e}")
            st.rerun()

        write_footnote(short_version=True)
