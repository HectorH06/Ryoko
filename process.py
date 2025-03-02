import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from scraper import run

orig = "Guadalajara"
dest = "Mexico City"

base_dir = "Ryokou"
full_path = os.path.join(base_dir, dest)
if not os.path.exists(full_path):
    os.makedirs(full_path)

# Itinerario
sched = [orig, dest, (datetime.now() + timedelta(days=1)).strftime('%m-%d-%Y'), '01-01-2025']
depart = datetime.strptime(sched[2], '%m-%d-%Y')

# Iterar hasta 300 días desde mañana
for departure_days in range(1, 300): 
    depart_date = depart + timedelta(days=departure_days)
    sched[2] = depart_date.strftime('%m-%d-%Y')
    
    # 14 a 31 días para la fecha de retorno
    for return_offset in [15, 31]:
        return_date = depart_date + timedelta(days=return_offset)
        sched[3] = return_date.strftime('%m-%d-%Y')
        
        with sync_playwright() as playwright:
            flight_data = run(sched, playwright)
        
        top_flights = flight_data.get('top_departing_flights', [])
        other_flights = flight_data.get('other_departing_flights', [])
        
        all_flights = top_flights + other_flights
        
        if not all_flights:
            print(f"No se encontraron vuelos para salida {sched[2]} y retorno {sched[3]}.")
        else:
            df_flights = pd.DataFrame(all_flights)
            df_flights['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_flights['days'] = return_offset
            df_flights['partida'] = sched[2]
            df_flights['regreso'] = sched[3] 
            
            file_name = os.path.join(full_path, f'{dest}.xlsx')
            
            if os.path.exists(file_name):
                existing_df = pd.read_excel(file_name)
                df_flights = pd.concat([existing_df, df_flights], ignore_index=True)
            df_flights.to_excel(file_name, index=False)