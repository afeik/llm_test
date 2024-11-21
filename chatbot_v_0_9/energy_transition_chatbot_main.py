
import streamlit as st 
import anthropic  # Importing the Claude AI client
from pathlib import Path
import streamlit_analytics2

# Import Page Components and Utils
from components.user_ratings import get_initial_rating, get_final_rating
from components.front_page import select_proficiency_level
from components.ai_conversation import claude_conversation
from components.footnote import write_footnote
from components.user_summary import get_user_statement_and_summary
from components.utils import set_background_color, language_dropdown

# Initialize Claude client
anthropic_api_key = st.secrets["claude"]["claude_auth"]
claude_client = anthropic.Client(api_key=anthropic_api_key)

st.session_state.lang = "de"
st.session_state.locale_dir = Path(__file__).parent / "components" / "languages"

# Change background color to dark petrol (ETH Color)
set_background_color("#FFFFFF")

with streamlit_analytics2.track():
    ### Main App Flow ### 
    if "step" not in st.session_state:
        #send_ga_event("page_view")
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
        _, col = language_dropdown(ret_cols=True)
        with col: 
            if st.button(_("Try Again?")):
                #send_ga_event("try_again")
                st.session_state.clear()
                st.rerun()

        st.write(_("<h4>Thank you for participating in the conversation!</h4>"),unsafe_allow_html=True)
        st.write(_("If you have further questions feel free to contact us:"))
        st.write(_("Dr. Mengshuo Jia (PSL - ETH Zürich) jia@eeh.ee.ethz.ch"))
        st.write(_("Benjamin Sawicki (NCCR Automation) bsawicki@ethz.ch"))
        st.write(_("Andreas Feik (ETH Zürich) anfeik@ethz.ch"))
        write_footnote(short_version=True)




