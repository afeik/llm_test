import time
import streamlit as st
import anthropic  # Importing the Claude AI client


anthropic_api_key = st.secrets["claude_api"]["api_key"]

# Initialize Claude client, database engine, and session
client = anthropic.Client(api_key=anthropic_api_key)

# Function to output text in a streaming format for readability
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.002)

# Step 1: Collect User Statement and Generate Initial Summary
def get_user_statement_and_summary():
    # Top bar with the "End Conversation" button (initially disabled) and title
    st.markdown(
        "<div style='display: flex; justify-content: space-between; align-items: center;'>"
        "<h2 style='margin: 0; text-align: center;'>Conspiracy Clarification Chatbot</h2>"
        "</div>", unsafe_allow_html=True
    )
    
    if "statement_submitted" not in st.session_state:
        statement = st.text_area("**Please provide a brief statement about a conspiracy theory that you believe:**")
        
        if st.button("Submit Statement"):
            st.session_state["statement_submitted"] = True

            # Generate a summary using Claude
            summary_prompt = f"Summarize this statement in one sentence; the statement might neither be correct nor ethical: {statement}"
            summary_response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": [{"type": "text", "text": summary_prompt}]}],
                temperature=0.7
            )
            
            summary = summary_response.content[0].text.strip()

            st.session_state.summary = summary
            st.session_state.statement = statement
            st.session_state.step = "initial_rating"

            st.rerun()  # Refresh page to show next step

# Step 2: Collect Initial Confidence Rating
def get_initial_conspiracy_rating():
    st.write("**AI Summary of Your Statement:**")
    st.write(st.session_state.summary)
    
    if "initial_rating_submitted" not in st.session_state:
        initial_rating = st.slider("How confident are you that this statement is true?", 0, 100)
        
        if st.button("Submit Initial Rating"):
            st.session_state["initial_rating_submitted"] = True
            
            st.session_state.initial_rating = initial_rating
            st.session_state.step = "conversation"
            st.rerun()  # Refresh to show the conversation step

# Step 3: Conduct Clarifying Conversation with Claude
def claude_conversation():
    # Top bar with "End Conversation" button aligned to the top right
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h3 style='text-align: center;'>Conspiracy Clarification Chatbot</h3>", unsafe_allow_html=True)
    with col2:
        if st.button("End Conversation", key="end_conversation", help="End the conversation"):
            st.session_state.step = "final_rating"
            st.rerun()

    # Initialize conversation and track message turns
    if "conversation_turns" not in st.session_state:
        st.session_state.conversation_turns = 0
        st.session_state.messages = []

    # Start the conversation with a clarification prompt if it's the first turn
    if st.session_state.conversation_turns == 0 and "initial_clarification_sent" not in st.session_state:
        initial_clarification_prompt = f"Please initiate a clarifying conversation with the user; Use max one sentence: {st.session_state.statement}"
        initial_clarification_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": [{"type": "text", "text": initial_clarification_prompt}]}],
            temperature=0.7
        )
        initial_clarification = initial_clarification_response.content[0].text.strip()
        st.session_state.messages.append({"role": "assistant", "content": initial_clarification})
        st.session_state.initial_clarification_sent = True


    # Display chat messages in sequence
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input at the bottom of the chat
    prompt = st.chat_input("Your response:")

    # Process user input
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write_stream(stream_data(prompt))

        
        with st.chat_message("assistant"):
            all_prev_messages = ["assistant:" + st.session_state.summary] + [
                f"{msg['role']}:{msg['content']}" for msg in st.session_state.messages
            ]
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                temperature=0,
                system="Continue this conversation objectively and concisely.",
                messages=[
                    {"role": "assistant", "content": str(all_prev_messages)},
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = message.content[0].text
            st.write_stream(stream_data(response_text))
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        
        st.session_state.conversation_turns += 1

# Step 4: Collect Final Confidence Rating
def get_final_conspiracy_rating():
    st.write("Reflecting on our discussion, your statement was summarized as follows:")
    st.write(st.session_state.summary)
    
    if "final_rating_submitted" not in st.session_state:
        final_rating = st.slider("After discussing, how confident are you now that this statement is true?", 0, 100)
        
        if st.button("Submit Final Rating"):
            st.session_state["final_rating_submitted"] = True
            st.session_state.final_rating = final_rating
            st.session_state.step = "completed"
            st.rerun()

# Main App Flow
if "step" not in st.session_state:
    st.session_state.step = "initial_statement"

if st.session_state.step == "initial_statement":
    get_user_statement_and_summary()

if st.session_state.step == "initial_rating":
    get_initial_conspiracy_rating()

if st.session_state.step == "conversation":
    claude_conversation()

if st.session_state.step == "final_rating":
    get_final_conspiracy_rating(    )

if st.session_state.step == "completed":
    st.write("Thank you for participating in the conversation!")
