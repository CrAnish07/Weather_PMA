# Weather_PMA
A streamlit based weather app that provides current conditions and a 5-day forecast. This app also supports persistent storage with CRUD, data exports(CSV)

- Get current weather using:
  - City or town names
  - Zip/Postal codes
  - Landmarks (e.g., Eiffel Tower)
  - GPS coordinates (latitude,longitude)
  - Or current location via IP address
    
- 5-Day Forecast

- Database-backed CRUD system:
  - **Create**: Save weather data with a date range
  - **Read**: View all stored entries
  - **Update**: Edit saved entries
  - **Delete**: Remove entries

- Export Data to:
  - CSV
    
## Setup Instructions

1. **Clone the repo**
    ```bash
    git clone https://github.com/CrAnish07/Weather_PMA.git
    ```
    ```bash
    cd Weather_PMA
    ```

2. **Install requirements**
      ```bash
      pip install -r requirements.txt
      ```

3. **Add your OpenWeather API Key: **
      get your actual api key from `https://home.openweathermap.org/api_keys`
      then add your actual api key at `.env` file
   ```bash
   OPENWEATHER_API_KEY=your_actual_api_key
   ```

5. **Run the Streamlit App**
   ```bash
   streamlit run weather_app.py
   ```
