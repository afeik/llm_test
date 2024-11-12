import streamlit as st
from .footnote import write_footnote
from .db_communication import update_proficiency
from .utils import get_image_path
from PIL import Image

# Function that queries the experience level of the user regarding the energy transition
def select_proficiency_level():
    """
    Prompts the user to select their experience level with the energy transition.

    This function presents three options for users to self-assess their proficiency 
    level regarding the energy transition: beginner, intermediate, and expert. 
    The selection will help tailor subsequent conversations according to the user's 
    background knowledge.
    """
    
    # Create a placeholder for the initial rating step
    placeholder = st.empty()

    with placeholder.container():

        st.markdown("<h2>Welcome to the Energy Transition Chatbot! </h2>", unsafe_allow_html=True)
        # Load and display the image
        image_path = get_image_path("energy_transition_switzerland.png")
        image = Image.open(image_path)
        st.image(image, use_column_width=True)
        st.write("How experienced are you with the energy transition? ")

        if "proficiency_selected" not in st.session_state:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("I've never heard of it."):
                    st.session_state.proficiency = "beginner"
                    st.session_state.proficiency_selected = True
                    st.session_state.step = "initial_statement"
                    placeholder.empty()
                    update_proficiency()
                    st.rerun()
            with col2:
                if st.button("I know the basics."):
                    st.session_state.proficiency = "intermediate"
                    st.session_state.proficiency_selected = True
                    st.session_state.step = "initial_statement"
                    placeholder.empty()
                    update_proficiency()
                    st.rerun()
            with col3:
                if st.button("I am an expert."):
                    st.session_state.proficiency = "expert"
                    st.session_state.proficiency_selected = True
                    st.session_state.step = "initial_statement"
                    placeholder.empty()
                    update_proficiency()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        write_footnote(short_version=True)