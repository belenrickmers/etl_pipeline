import os

from dotenv import load_dotenv

def load_env_variables():
    """
    Loads environment variables from the .env file.
    """
    load_dotenv()
    
def get_db_connection_string():
    """
    Constructs the database connection string from environment variables.
    """
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    if not all([host, port, db_name, user, password]):
        raise ValueError("Database connection environment variables are not fully set")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"