import streamlit as st
import gettext
from .utils import stream_data, get_chatbot_config,language_dropdown
from .footnote import write_footnote
from .db_communication import insert_db_message

chatbot_config = get_chatbot_config()


# Step 3: Conduct Clarifying Conversation with Claude
def claude_conversation(client):
    """
    Facilitates a conversational interface with Claude, a chatbot model, 
    to discuss the topic of the Energy Transition interactively with the user.

    This function initiates and manages a chat-style conversation where the user 
    and Claude can exchange messages. The conversation is displayed within a Streamlit 
    interface, and user interactions are logged to a database.

    Parameters:
    ----------
    client : object
        An instance of the Claude client for sending and receiving messages from 
        the Claude chatbot model.

    Workflow:
    ---------
    - Sets up the conversation layout, including a top bar with an "End Conversation" button.
    - Initializes the conversation by prompting Claude for an initial clarification 
      based on a user-provided statement.
    - Displays all previous messages in the conversation, including both user and 
      assistant responses, and appends new messages as they occur.
    - Processes user input from a chat-style input box:
        - Sends the user's message to the Claude model.
        - Appends the response from Claude to the conversation display and database.
    - Handles the conversation's end by switching to the final rating state.
    """
    _, col = language_dropdown(ret_cols = True)
    # Add end conversation button in the upper right corner
    with col: 
        if st.button(_("End Conversation"), key="end_conversation"):
            st.session_state.step = "final_rating"
            st.rerun()
    
    if st.session_state.lang == "de":
        disclaimer = chatbot_config["disclaimer_de"]
    else:
        disclaimer = chatbot_config["disclaimer_en"]

    # Top bar with "End Conversation" button aligned to the top right
    with st.container(height=720, border=False):

        # Initialize conversation and track message turns
        if "conversation_turns" not in st.session_state:
            st.session_state.conversation_turns = 0
            st.session_state.messages = []
        if st.session_state.lang == "de":
            lang_prompt = "Use German"
        else: 
            lang_prompt = "Use English"

        # Start the conversation with a clarification prompt if it's the first turn
        if st.session_state.conversation_turns == 0 and "initial_clarification_sent" not in st.session_state:
            
            initial_clarification_prompt = f"Please initiate a clarifying conversation with the user; Use max one sentence: {st.session_state.statement}"
            initial_clarification_response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=chatbot_config[st.session_state.proficiency]["conversation_max_tokens"],
                temperature=chatbot_config[st.session_state.proficiency]["conversation_temperature"],
                system = lang_prompt + chatbot_config["general"]["general_role"]  + chatbot_config[st.session_state.proficiency]["conversation_role"],
                messages=[{"role": "user", "content": [{"type": "text", "text": initial_clarification_prompt}]}],
            )
            
            initial_clarification = initial_clarification_response.content[0].text.strip()
            st.session_state.messages.append({"role": "assistant", "content": initial_clarification})
            st.session_state.initial_clarification_sent = True
            
            # Insert to DB 
            insert_db_message(initial_clarification, role = "assistant", message_type = "initial_clarification")

        disp_messages = st.container(height=620,border=False)

       # Display chat messages in sequence
        with disp_messages:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])


        st.markdown(
            f"""
            <div style='color: gray; font-size: 13px'>
                {disclaimer}
            </div>
            """,
            unsafe_allow_html=True
        )        # User input at the bottom of the chat
        prompt = st.chat_input(_("Your response:"))


        if prompt:
            with disp_messages:
                with st.chat_message("user"):
                    st.write_stream(stream_data(prompt))
            
            # Write message to database
            insert_db_message(prompt, role="user", message_type = "conversation")
            
            # Insert user input to session - state messages 
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Include all previous messages as context for the model
            all_prev_messages = ["assistant:" + st.session_state.summary] + [
                f"{msg['role']}:{msg['content']}" for msg in st.session_state.messages
            ]
            # Claude Query
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens= chatbot_config[st.session_state.proficiency]["conversation_max_tokens"],
                temperature= chatbot_config[st.session_state.proficiency]["conversation_temperature"],
                system = lang_prompt + chatbot_config["general"]["general_role"]  + chatbot_config[st.session_state.proficiency]["conversation_role"],
                messages=[
                    {"role": "assistant", "content": str(all_prev_messages)},
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            # Insert Claude Response to Database 
            insert_db_message(response_text, role = "assistant", message_type = "conversation")

            # Write out Claude Response
            with disp_messages:
                with st.chat_message("assistant"):
                    st.write_stream(stream_data(response_text))

            st.session_state.messages.append({"role": "assistant", "content": response_text})  
            st.session_state.conversation_turns += 1

    write_footnote(short_version=True)