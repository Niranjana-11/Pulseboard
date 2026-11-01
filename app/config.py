import os                                   # read environment variables
from dotenv import load_dotenv              # loads the .env file
from sqlalchemy.engine import URL           # builds a database URL safely

load_dotenv()                               # copy .env values into os.environ

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",       # database type + Python driver
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),   # 'localhost' from your laptop
    port=int(os.getenv("POSTGRES_PORT", 5432)),     # env values are text, so convert
    database=os.getenv("POSTGRES_DB"),
)