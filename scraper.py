from playwright.sync_api import sync_playwright
from selectolax.lexbor import LexborHTMLParser
import json, time


def get_page(playwright, from_place, to_place, departure_date, return_date):
    browser = playwright.chromium.launch(headless=True, args=["--window-position=-10000,-10000"])
    #browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.google.com/travel/flights?hl=en-US&curr=MXN')

    # type "From"
    impatience = 0.3
    patience = 1.5
    from_place_field = page.query_selector_all('.e5F5td')[0]
    from_place_field.click()
    time.sleep(impatience)
    from_place_field.type(from_place)
    time.sleep(impatience)
    page.keyboard.press('Enter')

    # type "To"
    to_place_field = page.query_selector_all('.e5F5td')[1]
    to_place_field.click()
    time.sleep(impatience)
    to_place_field.type(to_place)
    time.sleep(impatience)
    page.keyboard.press('Enter')

    # type "Departure date"
    departure_date_field = page.query_selector_all('[aria-label="Departure"]')[0]
    departure_date_field.click()
    time.sleep(impatience)
    departure_date_field.type(departure_date)
    time.sleep(impatience)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    time.sleep(impatience)

    # type "Return date"
    return_date_field = page.query_selector_all('[aria-label="Return"]')[0]
    return_date_field.click()
    time.sleep(impatience)
    return_date_field.type(return_date)
    time.sleep(impatience)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    time.sleep(impatience)

    # press "Explore"
    page.query_selector('.MXvFbd .VfPpkd-LgbsSe').click()
    time.sleep(patience)

    # press "More Flights"
    if type(page.query_selector('.ZVk93d button')) is 'NoneType':
        page.query_selector('.ZVk93d button').click()
        time.sleep(patience)

    parser = LexborHTMLParser(page.content())
    page.close()
    browser.close()

    return parser # takes between 8 and 10 seconds per page with those values for time.sleep when scraping massively


def scrape_google_flights(parser):
    data = {}

    categories = parser.root.css('.zBTtmb')
    category_results = parser.root.css('.Rk10dc')

    for category, category_result in zip(categories, category_results):
        category_data = []

        for result in category_result.css('.yR1fYc'):
            date = result.css('[jscontroller="cNtv4b"] span')
            departure_date = date[0].text()
            arrival_date = date[1].text()
            company = result.css_first('.Ir0Voe .sSHqwe').text()
            duration = result.css_first('.AdWm1c.gvkrdb').text()
            stops = result.css_first('.EfT7Ae .ogfYpf').text()
            emissions = result.css_first('.V1iAHe .AdWm1c').text()
            # emission_comparison = result.css_first('.N6PNV').text()
            price = result.css_first('.U3gSDe .FpEdX span').text()
            price_type = result.css_first('.U3gSDe .N872Rd').text() if result.css_first('.U3gSDe .N872Rd') else None

            flight_data = {
                'departure_date': departure_date,
                'arrival_date': arrival_date,
                'company': company,
                'duration': duration,
                'stops': stops,
                'emissions': emissions,
                # 'emission_comparison': emission_comparison,
                'price': price,
                'price_type': price_type
            }

            airports = result.css_first('.Ak5kof .sSHqwe')
            service = result.css_first('.hRBhge')

            if service:
                flight_data['service'] = service.text()
            else:
                flight_data['departure_airport'] = airports.css_first('span:nth-child(1) .eoY5cb').text()
                flight_data['arrival_airport'] = airports.css_first('span:nth-child(2) .eoY5cb').text()

            category_data.append(flight_data)

        data[category.text().lower().replace(' ', '_')] = category_data

    return data


def run(sched, playwright):
    from_place = sched[0]
    to_place = sched[1]
    departure_date = sched[2]
    return_date = sched[3]

    parser = get_page(playwright, from_place, to_place, departure_date, return_date)
    google_flights_results = scrape_google_flights(parser)

    if not google_flights_results:
        print("No se encontraron resultados de vuelos para la ruta especificada.")
        return {"message": "No flights found"}

    print(json.dumps(google_flights_results, indent=2, ensure_ascii=False))
    return google_flights_results
