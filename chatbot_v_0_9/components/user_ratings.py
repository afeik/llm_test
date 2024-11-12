import streamlit as st
from .footnote import write_footnote
from .db_communication import insert_final_rating, insert_initial_rating

def get_initial_rating():
    """
    Collects the user's initial confidence rating on the summarized statement.

    Displays a slider for the user to rate their confidence in the truth of a 
    summarized statement based on their initial input. Submits the rating to 
    the database and advances the conversation step.
    """
    # Create a placeholder for the initial rating step
    placeholder = st.empty()

    # Check if we're on the initial rating step
    if st.session_state.step == "initial_rating":
        with placeholder.container():
            st.write("**We've used AI to summarize your statement:**")
            st.write("\n")
            st.write("*\"" + st.session_state.summary + "\"*")
            st.write("\n")
            
            # Display the slider and submit button
            if "initial_rating_submitted" not in st.session_state:
                initial_rating = st.slider("How confident are you that this statement is true?", 0, 100)
                if st.button("Submit Initial Rating"):
                    # Insert to DB
                    insert_initial_rating(initial_rating)
                    st.session_state["initial_rating_submitted"] = True
                    st.session_state.initial_rating = initial_rating
                    st.session_state.step = "conversation"
                    placeholder.empty()
                    st.rerun()
                                  
                write_footnote()
    else:
        # Clear the placeholder if we're not on the initial rating step
        placeholder.empty()
    

def get_final_rating():
    """
    Collects the user's final confidence rating after the conversation.

    Displays the initial statement summary and provides a slider for the 
    user to rate their confidence after discussing it. Submits the rating 
    to the database and completes the conversation.
    """
    st.write("Reflecting on our discussion, your initial statement was summarized as follows:")
    st.write("\n")
    st.write("*\"" + st.session_state.summary + "\"*")
    st.write("\n")
    if "final_rating_submitted" not in st.session_state:
        final_rating = st.slider("After discussing, how confident are you now that this statement is true?", 0, 100)
        if st.button("Submit Final Rating"):
            # Insert to DB
            insert_final_rating(final_rating)
            st.session_state["final_rating_submitted"] = True
            st.session_state.final_rating = final_rating
            st.session_state.step = "completed"
            st.rerun()
    
    write_footnote(short_version=True)
