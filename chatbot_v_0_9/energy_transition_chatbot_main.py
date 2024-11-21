import streamlit as st
import anthropic
from pathlib import Path
import streamlit_analytics2

# Import components
from components.user_ratings import get_initial_rating, get_final_rating
from components.front_page import select_proficiency_level
from components.ai_conversation import claude_conversation
from components.footnote import write_footnote
from components.user_summary import get_user_statement_and_summary
from components.utils import set_background_color, language_dropdown

# Initialize session state
if "lang" not in st.session_state:
    st.session_state.lang = "de"

if "locale_dir" not in st.session_state:
    st.session_state.locale_dir = Path(__file__).parent / "components" / "languages"

if "step" not in st.session_state:
    st.session_state.step = "select_proficiency"
    st.session_state.keywords = None

if "proficiency" not in st.session_state:
    st.session_state.proficiency = None

if "proficiency_selected" not in st.session_state:
    st.session_state.proficiency_selected = False

if "consent_given" not in st.session_state:
    st.session_state.consent_given = False

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None  # Or set a default value like ""


# Initialize Claude client
anthropic_api_key = st.secrets["claude"]["claude_auth"]
claude_client = anthropic.Client(api_key=anthropic_api_key)

with streamlit_analytics2.track():
    if st.session_state.step == "select_proficiency":
        select_proficiency_level()

    if st.session_state.step == "initial_statement":
        try:
            get_user_statement_and_summary(claude_client)
        except Exception as e:
            st.error(f"Error in initial statement: {e}")

    if st.session_state.step == "initial_rating":
        try:
            get_initial_rating()
        except Exception as e:
            st.error(f"Error in initial rating: {e}")

    if st.session_state.step == "conversation":
        try:
            claude_conversation(claude_client)
        except Exception as e:
            st.error(f"Error in conversation: {e}")

    if st.session_state.step == "final_rating":
        try:
            get_final_rating()
        except Exception as e:
            st.error(f"Error in final rating: {e}")

    if st.session_state.step == "completed":
        _, col = language_dropdown(ret_cols=True)
        with col:
            if st.button("Try Again?"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.markdown(_("<h4>Thank you for participating!</h4>"), unsafe_allow_html=True)
        st.write(_("If you have further questions, contact us:"))
        st.write("Dr. Mengshuo Jia (PSL - ETH Zürich) jia@eeh.ee.ethz.ch")
        st.write("Benjamin Sawicki (NCCR Automation) bsawicki@ethz.ch")
        st.write("Andreas Feik (ETH Zürich) anfeik@ethz.ch")
        write_footnote(short_version=True)
