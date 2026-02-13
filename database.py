import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# -------------------------
# LOAD DATABASE CREDENTIALS
# -------------------------
DB_USER = st.secrets["database"]["user"]
DB_PASS = st.secrets["database"]["password"]
DB_HOST = st.secrets["database"]["host"]
DB_PORT = st.secrets["database"]["port"]
DB_NAME = st.secrets["database"]["name"]

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -------------------------
# CREATE ENGINE
# -------------------------
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=280,
    connect_args={"ssl": {}},  # Required for cloud MySQL
)

# -------------------------
# CREATE SESSION FACTORY
# -------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------------
# CREATE TABLES (RUNS ON START)
# -------------------------
Base.metadata.create_all(bind=engine)