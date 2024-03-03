from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import secrets

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = secrets.token_hex(16)
# Database configuration
host = 'localhost'
user = 'root'
password = 'root'
database = 'sign_up_login'

# Database configuration
db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
cursor = db.cursor()

# Create users table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
db.commit()

@app.route('/')
def index():
    return render_template('coverpage.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insert user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user credentials
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # Set the user's username in the session
            session['username'] = username

            # Redirect to the search page
            return redirect(url_for('index_hostel'))
        else:
            return "Login failed. Invalid credentials."

    return render_template('login.html')
@app.route('/index_hostel', methods=['POST','GET'])
def index_hostel():
    return render_template('index_try_hostel.html')
@app.route('/search', methods=['POST'])
def search():
    location = request.form.get('location', '')
    data = hostels_nearby(location)
    return render_template('result.html', data=data)

def hostels_nearby(location):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    driver_path = "D:\\thumbnail scrapping\\chromedriver-win64\\chromedriver.exe"
    driver = webdriver.Chrome(driver_path, options=options)

    url = f"https://www.google.com/maps/search/hostels+near+{location}"
    driver.get(url)
    driver.maximize_window()

    data = list()
    initial_height = driver.execute_script(
        "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")

    def scroll_down_with_end_key():
        section = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
        section.send_keys(Keys.END)

    def click_and_open_tab(url):
        driver.execute_script("window.open('', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        driver.get(url)
        button_element = driver.find_element(By.XPATH,
                                              '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button')
        button_element.click()

        starting_point_locator = (By.XPATH, '//*[@id="sb_ifc50"]/input')
        starting_point = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(starting_point_locator))

        starting_point.click()
        starting_point.clear()
        starting_point.send_keys(f"{location}")

        search_button_locator = (By.XPATH, '//*[@id="directions-searchbox-0"]/button[1]')
        search_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(search_button_locator))
        search_button.click()

        travel_locator_locator = (By.XPATH, '//*[@id="section-directions-trip-title-0"]')
        travel_locator = WebDriverWait(driver, 3).until(EC.presence_of_element_located(travel_locator_locator))

        ans = set()

        for i in range(5):
            try:
                value = '//*[@id="section-directions-trip-title-' + str(i) + '"]'
                travel_locator = driver.find_element(By.XPATH, value)
                time.sleep(2)
                value = '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div[2]'
                distance_locator = driver.find_element(By.XPATH, value)
            except:
                continue

            ans.add((travel_locator.text, distance_locator.text))

        return list(ans)

    while True:
        scroll_down_with_end_key()
        time.sleep(1)

        for a in range(15):
            value = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[' + str(
                a) + ']/div/a'
            current_img = driver.find_elements(By.XPATH, value=value)

            for i in current_img:
                ans = click_and_open_tab(i.get_attribute('href'))
                driver.switch_to.window(driver.window_handles[0])

                if [i.get_attribute('aria-label'), ans] in data:
                    continue
                else:
                    data.append([i.get_attribute('aria-label'), ans])

                time.sleep(1)

        new_height = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        if new_height == initial_height:
            break

    initial_height = new_height

    data = list(data)
    driver.quit()
    return data

if __name__ == '__main__':
    app.run(debug=True)
