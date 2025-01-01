import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os

# Read environment variables for the date range
desired_start_date = os.getenv('DESIRED_START_DATE', '01/01/2025')
desired_end_date = os.getenv('DESIRED_END_DATE', '05/01/2025')

# Debug: Print out the values for start and end date
print(f"Start Date: {desired_start_date}")
print(f"End Date: {desired_end_date}")

# Gmail login credentials
gmail_user = 'project.mnagement2406@gmail.com'
gmail_password = 'zgnb cmko qzqw ewsx'

# Recipient's email
recipient_email = 'siai.wajih@hotmail.com'

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
url = "https://tickets.wbstudiotour.co.uk/webstore/shop/viewitems.aspx?c=tix2&cg=hptst2"
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# Increment ticket count to 3
for _ in range(3):
    add_ticket_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@aria-label='Increase quantity for  Adult Ages 16 years and above ']")
        )
    )
    add_ticket_button.click()

# Verify the counter reflects 3 tickets
counter = driver.find_element(By.XPATH, "//input[@ng-model='item.quantityInputEl.value']")
assert counter.get_attribute("value") == "3", "Counter did not update to 3 tickets."

# Open the date and time selection modal
date_modal_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[@ng-click='selectEvent(subCategory, shared, $index)']"))
)
date_modal_button.click()

# Wait for the modal to fully load
time.sleep(2)

# Convert the desired start and end dates from strings to datetime objects
try:
    desired_range_start = datetime.strptime(desired_start_date, "%d/%m/%Y")
    desired_range_end = datetime.strptime(desired_end_date, "%d/%m/%Y")
except ValueError as e:
    print(f"Error parsing dates: {e}")
    driver.quit()
    exit()

# Debug: Check if date parsing works as expected
print(f"Parsed Start Date: {desired_range_start}")
print(f"Parsed End Date: {desired_range_end}")

tickets_found = []

# Set the desired month and year
desired_month = "1"  # January
desired_year = "2025"

# Select the desired year
year_dropdown = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//select[@ng-model='viewModel.calendar.year']"))
)
year_options = year_dropdown.find_elements(By.TAG_NAME, "option")
for option in year_options:
    if option.get_attribute("value") == f"string:{desired_year}":
        option.click()
        break

# Select the desired month
month_dropdown = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//select[@ng-model='viewModel.calendar.month']"))
)
month_options = month_dropdown.find_elements(By.TAG_NAME, "option")
for option in month_options:
    if option.get_attribute("value") == f"string:{desired_month}":
        option.click()
        break

# Wait for the calendar to update
time.sleep(2)

# Scrape available dates
all_dates = wait.until(
    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'day')]"))
)
for date_element in all_dates:
    aria_label = date_element.get_attribute("aria-label")
    class_name = date_element.get_attribute("class")

    # Look for the "available" keyword in the class attribute
    if aria_label and "available" in class_name and "disabled" not in class_name:
        # Correctly parse the aria_label using the actual format 'dd/mm/yyyy'
        try:
            date = datetime.strptime(aria_label.strip(), "%d/%m/%Y")
            if desired_range_start <= date <= desired_range_end:
                tickets_found.append(date.strftime("%d/%m/%Y"))
        except ValueError:
            # If the date is not parsable, skip this entry
            continue

# Notify if tickets are found and send email
if tickets_found:
    available_dates = ', '.join(tickets_found)
    print(f"Tickets are available for the following dates: {available_dates}")
    
    # Send email notification
    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = 'Tickets Available Notification'

        body = f'Hurry up ! Tickets for Harry Potter studio tour :) are now available for the following dates : {available_dates}'
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, recipient_email, text)
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
else:
    print(f"No tickets available in the desired range from {desired_range_start.strftime('%d/%m/%Y')} to {desired_range_end.strftime('%d/%m/%Y')}")

# Close the browser
driver.quit()
