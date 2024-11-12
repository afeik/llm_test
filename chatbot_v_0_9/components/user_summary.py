import streamlit as st
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import io
from PIL import Image

from .footnote import write_footnote
from .db_communication import insert_db_message
from .utils import get_chatbot_config

chatbot_config = get_chatbot_config()

def get_user_statement_and_summary(client):
    """
    Collects a user statement, generates a summary using the Claude API, 
    and displays the summary for user confirmation.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h2>Switzerland's Energy Transition</h2>", unsafe_allow_html=True)
        statement = st.text_area("**Please describe a concrete concern that you have about the Energy Transition:**", height=200)
        
        min_char_count = 30
        char_count = len(statement)

        if st.button("Submit Statement"): 
            can_submit = char_count >= min_char_count
            if not can_submit:
                st.markdown(
                    f"""
                    <div style="background-color: #00596D; color: #f0f0f0; font-size: 13px">
                        Please enter at least {min_char_count} characters.
                        You currently have {char_count} characters.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                summary_response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=chatbot_config[st.session_state.proficiency]["summary_max_tokens"],
                    system=chatbot_config["general"]["general_role"] + chatbot_config[st.session_state.proficiency]["summary_role"],
                    messages=[{"role": "user", "content": [{"type": "text", "text": statement}]}],
                    temperature=chatbot_config[st.session_state.proficiency]["summary_temperature"]
                )
                
                summary = summary_response.content[0].text.strip()
                insert_db_message(statement, role="user", message_type="initial_statement")
                insert_db_message(summary, role="assistant", message_type="initial_statement_summary")
                
                st.session_state.summary = summary
                st.session_state.statement = statement
                st.session_state.step = "initial_rating"
                st.rerun()
                placeholder.empty()

    with st.expander("Do you need help formulating your concern? - Let AI give you some Keywords!"):
        if st.session_state.keywords is None:
            st.session_state.keywords = get_energy_transition_keywords(client)
            st.session_state.wordcloud_image = create_wordcloud_image(st.session_state.keywords)
            st.image(st.session_state.wordcloud_image, use_column_width=True)
        else:
            st.image(st.session_state.wordcloud_image, use_column_width=True)

    write_footnote()

def get_energy_transition_keywords(client):
    """
    Generates keywords related to energy transition using the Claude API.
    Returns a list of keywords.
    """
    keywords_prompt = chatbot_config["keyword_generation"]
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=chatbot_config[st.session_state.proficiency]["summary_max_tokens"],
        system=chatbot_config["general"]["general_role"] + chatbot_config[st.session_state.proficiency]["conversation_role"],
        messages=[{"role": "user", "content": [{"type": "text", "text": keywords_prompt}]}],
        temperature=chatbot_config[st.session_state.proficiency]["summary_temperature"]
    )
    keywords = response.content[0].text.strip()
    return keywords.split(", ")

def create_wordcloud_image(keywords):
    """
    Creates and returns a word cloud image from a list of keywords.
    """
    text = ' '.join(keywords)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    img = plt_to_image(fig)
    plt.close(fig)
    return img

def plt_to_image(fig):
    """
    Converts a Matplotlib figure to a PIL image and returns it.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return Image.open(buf)
