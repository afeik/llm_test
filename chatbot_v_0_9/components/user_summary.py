import streamlit as st
from .footnote import write_footnote
from .db_communication import insert_db_message, insert_full_conversation_details
from .utils import get_chatbot_config, language_dropdown

chatbot_config = get_chatbot_config()

def get_user_statement_and_summary(client):
    """
    Collects a user statement, generates a summary using the Claude API,
    and displays the summary for user confirmation, along with additional mandatory user details.
    """
    _ = language_dropdown()
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(
            _("<h4>Switzerland's Energy Transition</h4>"),
            unsafe_allow_html=True
        )

        # Age input with intervals
        st.session_state.age_group = st.selectbox(
            _("Age Group:"),
            [
                _("Select"),
                _("Under 18"),
                _("18-24"),
                _("25-34"),
                _("35-44"),
                _("45-54"),
                _("55-64"),
                _("65 and older"),
                _("Prefer not to say"),
            ],
            index=0
        )

        # Gender selection
        st.session_state.gender = st.selectbox(
            _("Gender:"),
            [_("Select"), _("Male"), _("Female"), _("other"), _("Prefer not to say")],
            index=0
        )

        # Highest Degree selection
        st.session_state.highest_degree = st.selectbox(
            _("Highest Degree Achieved:"),
            [_("Select"), _("High School"), _("Bachelor's"), _("Master's"), _("PhD"), _("Other")],
            index=0
        )

        # Display the text area for user input
        statement = st.text_area(
            _(
                "**Please describe a concrete concern that you have about the Energy Transition:**"
            ),
            height=200
        )

        # Create columns for the button and the error message
        col1, col2 = st.columns([1.5, 3.6])

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
        char_count = len(statement)

        # Ensure all fields are filled before submission
        fields_filled = (
            st.session_state.age_group != _("Select")
            and st.session_state.gender != _("Select")
            and st.session_state.highest_degree != _("Select")
            and char_count >= min_char_count
        )

        if submit_button:
            if not fields_filled:
                # Display appropriate error message
                with col2:
                    error_message = _(
                        "<div style='color: gray; font-size: 13px; padding: 5px; text-align: center; border-radius: 5px;'>"
                    )
                    if st.session_state.age_group == _("Select"):
                        error_message += _("Please select your age group.")
                    elif st.session_state.gender == _("Select"):
                        error_message += _("Please select your gender.")
                    elif st.session_state.highest_degree == _("Select"):
                        error_message += _("Please select your highest degree.")
                    elif char_count < min_char_count:
                        error_message += (
                            _("Please enter at least ")
                            + str(min_char_count)
                            + _(" characters. You currently have: ")
                            + str(char_count)
                            + _(" characters.")
                        )
                    error_message += "</div>"
                    error_placeholder.markdown(error_message, unsafe_allow_html=True)
            else:
                # Clear the error message if any
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
                insert_full_conversation_details(st.session_state.age_group,st.session_state.gender,
                                                 st.session_state.highest_degree,st.session_state.consent_given)

                st.session_state.summary = summary
                st.session_state.statement = statement
                st.session_state.step = "initial_rating"

                st.rerun()

    write_footnote()

