from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
DB_NAME = "weather.db"

class WeatherRecord(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True)
    location = Column(String)
    date = Column(Date)
    temperature = Column(Float)
    description = Column(String)

engine = create_engine(f"sqlite:///{DB_NAME}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
