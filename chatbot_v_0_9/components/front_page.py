import streamlit as st
from .footnote import write_footnote
from .db_communication import update_proficiency, init_db_communication
from .utils import get_image_path, language_dropdown
from PIL import Image
import streamlit_analytics

# Function that queries the experience level of the user regarding the energy transition
def select_proficiency_level():
    """
    Prompts the user to select their experience level with the energy transition.

    This function presents three options for users to self-assess their proficiency 
    level regarding the energy transition: beginner, intermediate, and expert. 
    The selection will help tailor subsequent conversations according to the user's 
    background knowledge.
    """
    
    _ = language_dropdown()

    # Create a placeholder for the initial rating step
    placeholder = st.empty()

    with streamlit_analytics.track():
        with placeholder.container():

            st.markdown(_("<h3>Welcome to the Energy Transition Chatbot!</h3>"), unsafe_allow_html=True)
            # Load and display the image
            image_path = get_image_path("energy_transition_switzerland.png")
            image = Image.open(image_path)
            st.image(image, use_column_width=True)

            proficiency_rating = st.slider(_("How experienced are you with the energy transition?"), 0, 100)

            if proficiency_rating >=0 and proficiency_rating<=33:
                st.session_state.proficiency = "beginner"
    
            elif proficiency_rating >33 and proficiency_rating<=66: 
                st.session_state.proficiency = "intermediate"

            elif proficiency_rating >66 and proficiency_rating<=100:
                st.session_state.proficiency = "expert"

            if st.button(_("Start Chatbot")): 
                st.session_state.proficiency_selected = True
                st.session_state.step = "initial_statement"
                placeholder.empty()
                init_db_communication()
                update_proficiency()
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

            write_footnote(short_version=True)