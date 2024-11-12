
import streamlit as st 
import anthropic  # Importing the Claude AI client

# Import Page Components and Utils
from components.user_ratings import get_initial_rating, get_final_rating
from components.front_page import select_proficiency_level
from components.ai_conversation import claude_conversation
from components.footnote import write_footnote
from components.user_summary import get_user_statement_and_summary
from components.utils import set_background_color
from components.db_communication import init_db_communication

# Initialize Claude client
anthropic_api_key = st.secrets["claude"]["claude_auth"]
claude_client = anthropic.Client(api_key=anthropic_api_key)

# Initialize Database Enty 
init_db_communication()

# Change background color to dark petrol (ETH Color)
set_background_color("#00596D")

### Main App Flow ### 
if "step" not in st.session_state:
    st.session_state.keywords = None
    st.session_state.step = "select_proficiency"

if st.session_state.step == "select_proficiency":
    select_proficiency_level()
    
if st.session_state.step == "initial_statement":
    get_user_statement_and_summary(claude_client)

if st.session_state.step == "initial_rating":
    get_initial_rating()

if st.session_state.step == "conversation":
    claude_conversation(claude_client)

if st.session_state.step == "final_rating":
    get_final_rating()

if st.session_state.step == "completed":
    st.write("**Thank you for participating in the conversation!**")
    st.write("If you have further questions feel free to contact us:")
    st.write("Dr. Mengshuo Jia (Power Systems Lab - ETH Zürich) jia@eeh.ee.ethz.ch")
    st.write("Benajmin Sawicki (NCCR Automation) bsawicki@ethz.ch")
    st.write("Andreas Feik (ETH Zürich) anfeik@ethz.ch")
    write_footnote(short_version=True)



