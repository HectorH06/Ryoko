import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from scraper import run

orig = "Guadalajara"
dest = "Tokyo"

sched = [orig, dest, "03-09-2025", "03-16-2025"]
with sync_playwright() as playwright:
            flight_data = run(sched, playwright)