import streamlit as st
from .footnote import write_footnote
from .db_communication import insert_db_message
from .utils import get_chatbot_config, language_dropdown,send_ga_event
import streamlit_analytics

chatbot_config = get_chatbot_config()

def get_user_statement_and_summary(client):
    """
    Collects a user statement, generates a summary using the Claude API,
    and displays the summary for user confirmation.
    """
    _ = language_dropdown()
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(
            _("<h3>Switzerland's Energy Transition</h3>"),
            unsafe_allow_html=True
        )

        # Display the text area for user input
        statement = st.text_area(
            _(
                "**Please describe a concrete concern that you have about the Energy Transition:**"
            ),
            height=200
        )

        # Create columns for the button and the error message
        col1, col2, col3 = st.columns([1.5, 3.6, 1])

        with col1:
            submit_button = st.button(_("Submit Concern"))
        with col2:
            error_placeholder = st.empty()

        # Example concerns to be displayed
        example_concerns = [
            _("I'm worried the energy transition will increase electricity bills."),
            _("I'm concerned about blackouts during the transition period."),
            _("I fear job losses in traditional energy sectors."),
            _("I'm worried about environmental impacts of new infrastructure."),
            _("I feel the transition is moving too fast and disrupting daily life."),
        ]


        # Create an expandable section for example concerns with smaller font size
        with st.expander(_("Need inspiration? Click here to see example concerns.")):
            for concern in example_concerns:
                st.markdown(
                    f"<p style='font-size:14px;color:grey;margin-bottom: 10px;'>- {concern}</p>",
                    unsafe_allow_html=True
                )

        min_char_count = 30
        char_count = len(statement)  # Using len(statement) as in the initial code

    
        if submit_button:
            can_submit = char_count >= min_char_count
            if not can_submit:
                #send_ga_event("initial_statement_too_few_characters")
                # Display the error message in the second column, next to the button
                with col2:
                    error_placeholder.markdown(
                        _(
                            """<div style="background-color: #000000; color: gray; font-size: 13px; padding: 5px; text-align: center; border-radius: 5px;">
                            Please enter at least """
                        ) + str(min_char_count) + _(
                            """ characters. You currently have: """
                        ) + str(char_count) + _(""" characters.</div>"""),
                        unsafe_allow_html=True
                    )
            else:
                # Clear the error message if any
                #send_ga_event("initial_statement_submitted")
                error_placeholder.empty()
                if st.session_state.lang == "de":
                    lang_prompt = "Use German"
                else:
                    lang_prompt = "Use English"

                summary_response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=chatbot_config[st.session_state.proficiency][
                        "summary_max_tokens"
                    ],
                    system=lang_prompt
                    + chatbot_config[st.session_state.proficiency]["summary_role"],
                    messages=[
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": statement}],
                        }
                    ],
                    temperature=chatbot_config[st.session_state.proficiency][
                        "summary_temperature"
                    ],
                )
                placeholder.empty()
                summary = summary_response.content[0].text.strip()
                insert_db_message(
                    statement, role="user", message_type="initial_statement"
                )
                insert_db_message(
                    summary, role="assistant", message_type="initial_statement_summary"
                )

                st.session_state.summary = summary
                st.session_state.statement = statement
                st.session_state.step = "initial_rating"
                
                st.rerun()
                

    write_footnote()



