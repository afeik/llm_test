# db_functions.py

from datetime import datetime
import streamlit as st
from sqlalchemy.sql import insert, update
from sqlalchemy.exc import SQLAlchemyError

# Import database session and table definitions from db.py
from .db import Session, conversations, messages
from .utils import get_chatbot_config

# Load chatbot configuration
chatbot_config = get_chatbot_config()

def init_db_communication():
    """Initialize a new conversation if none exists in session_state."""
    if "conversation_id" not in st.session_state:
        session = Session()
        try:
            result = session.execute(
                insert(conversations).values(
                    start_time=datetime.now(),
                    chatbot_version=chatbot_config["version"],
                    usecase=chatbot_config["usecase"]
                )
            )
            st.session_state.conversation_id = result.inserted_primary_key[0]
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            st.error(f"Database error during conversation initialization: {e}")
        finally:
            session.close()

def insert_db_message(message, role, message_type):
    """Insert a message into the messages table."""
    session = Session()
    try:
        session.execute(
            insert(messages).values(
                conversation_id=st.session_state.conversation_id,
                role=role,
                content=message,
                message_type=message_type,
                timestamp=datetime.now()
            )
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Database error during message insertion: {e}")
    finally:
        session.close()

def insert_initial_rating(rating):
    """Insert the initial rating for a conversation."""
    session = Session()
    try:
        session.execute(
            update(conversations).where(
                conversations.c.conversation_id == st.session_state.conversation_id
            ).values(initial_rating=rating)
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Database error during initial rating insertion: {e}")
    finally:
        session.close()

def insert_final_rating(rating):
    """Insert the final rating for a conversation."""
    session = Session()
    try:
        session.execute(
            update(conversations).where(
                conversations.c.conversation_id == st.session_state.conversation_id
            ).values(final_rating=rating)
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Database error during final rating insertion: {e}")
    finally:
        session.close()

def update_proficiency():
    """Update the proficiency level for a conversation."""
    session = Session()
    try:
        session.execute(
            update(conversations).where(
                conversations.c.conversation_id == st.session_state.conversation_id
            ).values(proficiency=st.session_state.proficiency)
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Database error during proficiency update: {e}")
    finally:
        session.close()
