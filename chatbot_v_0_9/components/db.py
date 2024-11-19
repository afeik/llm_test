# db.py

from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import streamlit as st

# Load database URI from Streamlit secrets
db_uri = st.secrets["neon_db"]["db_uri"]

# Ensure that db_uri includes 'sslmode=require'
if 'sslmode' not in db_uri:
    if '?' in db_uri:
        db_uri += '&sslmode=require'
    else:
        db_uri += '?sslmode=require'

# Initialize Metadata and Database Tables
metadata = MetaData()

# Define tables
conversations = Table(
    'conversations', metadata,
    Column('conversation_id', Integer, primary_key=True, autoincrement=True),
    Column('start_time', TIMESTAMP, default=datetime.now),
    Column('initial_rating', Integer),
    Column('final_rating', Integer),
    Column('proficiency', String(20)),
    Column('chatbot_version', String(20)),
    Column('usecase', String(20))
)

messages = Table(
    'messages', metadata,
    Column('message_id', Integer, primary_key=True, autoincrement=True),
    Column('conversation_id', Integer, ForeignKey('conversations.conversation_id')),
    Column('role', String(20), nullable=False),
    Column('content', Text, nullable=False),
    Column('timestamp', TIMESTAMP, default=datetime.now),
    Column('message_type', String(50))
)

# Initialize Database Engine and Session Factory
engine = create_engine(
    db_uri,
    connect_args={"sslmode": "require"},
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections every 30 minutes
)
Session = scoped_session(sessionmaker(bind=engine))

# Remove or comment out the following line to prevent recreating tables on each run
# metadata.create_all(engine)
