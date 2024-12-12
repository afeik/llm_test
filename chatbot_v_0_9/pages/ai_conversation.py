import streamlit as st
from components.utils import stream_data, get_chatbot_config, language_dropdown
from components.footnote import write_footnote
from components.db_communication import insert_db_message

st.set_page_config("Solar Energy Chatbot",":robot_face:")
chatbot_config = get_chatbot_config()


if "page_set" not in st.session_state:
    # If not, set it to the main page and reload
    st.switch_page("energy_transition_chatbot_main.py")

def claude_conversation(client):
    """
    Facilitates a conversational interface with Claude, a chatbot model, 
    to discuss the topic of the Energy Transition interactively with the user.

    Parameters:
    ----------
    client : object
        An instance of the Claude client for sending and receiving messages from 
        the Claude chatbot model.
    """

    # Language selection and "End Conversation" button in top right
    lang = st.session_state.lang
    _, col = language_dropdown(lang,ret_cols=True)
    with col:
        if st.button(_("Provide Final Feedback"), key="end_conversation"):
            st.switch_page("./pages/user_ratings.py")
            #st.session_state.step = "final_rating"
            st.rerun()

    # Set disclaimer based on language
    disclaimer = chatbot_config["disclaimer_de"] if st.session_state.lang == "de" else chatbot_config["disclaimer_en"]

    # Initialize session state variables
    if "conversation_turns" not in st.session_state:
        st.session_state.conversation_turns = 0
        st.session_state.messages = []

    # Determine language prompt and solar prompt
    lang_prompt = "Verwende die Deutsche Sprache." if st.session_state.lang == "de" else "Use the English Language."
    solar_prompt = (
        f"Solar Ownership: {st.session_state.solar_panel_ownership}. "
        f"Based on this, emphasize these questions (concise and not all at once): "
        f"{chatbot_config['solar_ownership'][st.session_state.solar_panel_ownership]['questions']}"
        f"User Proficiency Level: {st.session_state.proficiency}"
    )

    # Main conversation container (similar to original code)
    with st.container(height=630, border=False):
        # If it's the first turn, get initial clarification from Claude
        if st.session_state.conversation_turns == 0 and "initial_clarification_sent" not in st.session_state:
            with st.spinner(_("Preparing your conversation ...")):
                initial_clarification_response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=chatbot_config[st.session_state.proficiency]["conversation_max_tokens"],
                    temperature=chatbot_config[st.session_state.proficiency]["conversation_temperature"],
                    system=f"{lang_prompt} If German, you can use a Swiss Greeting like Grüezi or similar {chatbot_config['general']['general_role']} {chatbot_config[st.session_state.proficiency]['conversation_role']}",
                    messages=[{"role": "user", "content": solar_prompt}],
                )

            initial_clarification = initial_clarification_response.content[0].text.strip()
            st.session_state.messages.append({"role": "assistant", "content": initial_clarification})
            st.session_state.initial_clarification_sent = True

            # Insert initial clarification to DB
            insert_db_message(initial_clarification, role="assistant", message_type="conversation")

        # Container for displaying messages, similar dimensions as original
        disp_messages = st.container(height=520,border=False)
        with disp_messages:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Display disclaimer below messages, just like in the original code
        st.markdown(
            f"""
            <div style='color: gray; font-size: 13px'>
                {disclaimer}
            </div>
            """,
            unsafe_allow_html=True
        )

        # User input at the bottom
        user_input = st.chat_input(_("Your response:"))
        if user_input:
            # Display user input
            with disp_messages:
                with st.chat_message("user"):
                    st.write_stream(stream_data(user_input))

            # Insert user's message into DB
            insert_db_message(user_input, role="user", message_type="conversation")
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Prepare context for Claude
            context_messages = [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]

            # Get Claude's response
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=chatbot_config[st.session_state.proficiency]["conversation_max_tokens"],
                temperature=chatbot_config[st.session_state.proficiency]["conversation_temperature"],
                system=f"{lang_prompt} {chatbot_config['general']['general_role']} {chatbot_config[st.session_state.proficiency]['conversation_role']} {solar_prompt}",
                messages=[
                    {"role": "assistant", "content": "\n".join(context_messages)},
                    {"role": "user", "content": user_input},
                ],
            )

            response_text = response.content[0].text.strip()
            insert_db_message(response_text, role="assistant", message_type="conversation")

            # Display Claude's response
            with disp_messages:
                with st.chat_message("assistant"):
                    st.write_stream(stream_data(response_text))

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.session_state.conversation_turns += 1

    # Footnote at the bottom of the page, outside the main conversation container
    write_footnote(short_version=False)

claude_conversation(st.session_state.claude_client)
