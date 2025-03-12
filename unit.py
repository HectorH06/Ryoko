import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from scraper import run

orig = "Guadalajara"
dest = "Tokyo"

base_dir = "Ryokou"
full_path = os.path.join(base_dir, dest)

# Search a single flight

sched = [orig, dest, "08-01-2025", "08-08-2025"]
date_format = "%m-%d-%Y"
start_date = datetime.strptime(sched[2], date_format)
end_date = datetime.strptime(sched[3], date_format)

return_offset = (end_date - start_date).days

with sync_playwright() as playwright:
    flight_data = run(sched, playwright)

    top_flights = flight_data.get('top_departing_flights', [])
    other_flights = flight_data.get('other_departing_flights', [])
    
    all_flights = top_flights + other_flights
    
    df_flights = pd.DataFrame(all_flights)
    df_flights['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_flights['days'] = return_offset
    df_flights['partida'] = sched[2]
    df_flights['regreso'] = sched[3] 
    
    file_name = os.path.join(full_path, f'{dest}.xlsx')
    
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        df_flights = pd.concat([existing_df, df_flights], ignore_index=True)
    df_flights.to_excel(file_name, index=False)
