# Importing libraries
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
pd.options.mode.chained_assignment = None
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Function to delay some process
def delay():
    time.sleep(random.randint(3, 10))

# Scrolling down the page in order to overcome Lazy Loading
def lazy_loading():
    element = driver.find_element(By.TAG_NAME, 'body')
    count = 0
    while count < 20:
        element.send_keys(Keys.PAGE_DOWN)
        delay()
        count += 1

# Function to fetch the product links of products
def fetch_product_links_and_ranks():
    try:
        # Wait for the product grid to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "p13n-desktop-grid")))
        
        # Once the product grid is present, proceed with extracting product links and rankings
        content = driver.page_source
        homepage_soup = BeautifulSoup(content, 'html.parser')
    
        all_products = homepage_soup.find('div', attrs={"class": "p13n-desktop-grid"})
        
        if all_products is not None:
            for product_section in all_products.find_all('div', {'id': 'gridItemRoot'}):
                for product_link in product_section.find_all('a',{'tabindex':'-1'}):
                    if product_link['href'].startswith('https:'):
                        product_links.append(product_link['href'])
                    else:
                        product_links.append('https://www.amazon.com' + product_link['href'])
                ranking.append(product_section.find('span',{'class': 'zg-bdg-text'}).text)
        else:
            print("No products found on the page.")
    except Exception as e:
        print("An error occurred while fetching product links and ranks:", str(e))

# Function to extract content of the page
def extract_content(url):
    driver.get(url)
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    return product_soup

# Function to extract product name
def extract_product_name(soup):
    try:
        name_of_product = soup.find('div', attrs={"id": "titleSection"}).text.strip()
        data['product name'].iloc[product] = name_of_product

    except:
        name_of_product = 'Product name not available '
        data['product name'].iloc[product] = name_of_product

# Function to extract brand name
def extract_brand(soup):
    try:
        brand = soup.find('a', attrs={"id": "bylineInfo"}).text.split(':')[1].strip()  #one location where brand data could be found
        data['brand'].iloc[product] = brand

    except:
        if soup.find_all('tr', attrs={'class': 'a-spacing-small po-brand'}):  #other location where brand data could be found
            brand = soup.find_all('tr', attrs={'class': 'a-spacing-small po-brand'})[0].text.strip().split(' ')[-1]
            data['brand'].iloc[product] = brand
        else:
            brand = 'Brand data not available'
            data['brand'].iloc[product] = brand

def extract_price(soup):
    try:
        # Find the element containing the price
        price_element = soup.find('span', class_='a-offscreen')

        # Extract the price text from the element
        price_text = price_element.text.strip()

        # Extract the price value
        price = price_text.split('$')[-1]

        # Update the 'price(in dollar)' column in the DataFrame
        data['price(in dollar)'].iloc[product] = price
    except Exception as e:
        # If an error occurs, set the price to 'Price data not available'
        price = 'Price data not available'
        data['price(in dollar)'].iloc[product] = price
        print("Error while extracting price:", e)



# Function to extract size
def extract_size(soup):
    try:
        size = soup.find('span', attrs={"id": "inline-twister-expanded-dimension-text-size_name"}).text.strip()
        data['size'].iloc[product] = size

    except:
        size = 'Size data not available'
        data['size'].iloc[product] = size

# Function to extract star rating
def extract_star_rating(soup):
    try:
        star = None
        for star_rating_locations in ['a-icon a-icon-star a-star-4-5', 'a-icon a-icon-star a-star-5']:
            stars = soup.find_all('i', attrs={"class": star_rating_locations})
            for i in range(len(stars)):
                star = stars[i].text.split(' ')[0]
                if star:
                    break
            if star:
                break
        
    except:
        star = 'Star rating data not available'
        
    data['star rating'].iloc[product] = star   

# Function to extract number of ratings
def extract_num_of_ratings(soup):
    try:
        star = soup.find('span', attrs={"id": "acrCustomerReviewText"}).text.split(' ')[0]
        data['number of ratings'].iloc[product] = star

    except:
        star = 'Number of rating not available'
        data['number of ratings'].iloc[product] = star

# Function to extract color
def extract_color(soup):
    try:
        color = soup.find('tr', attrs={'class': 'a-spacing-small po-color'}).text.strip().split('  ')[1].strip()
        data['color'].iloc[product] = color

    except:
        color = 'Color not available'
        data['color'].iloc[product] = color


# Fetching the product links of all items
product_links = []
ranking=[]


for page in range(1, 3):  # Iterate over the 2 pages in which the products are divided
    fetch_product_links_and_ranks()  # To fetch the links to products
    # Update the URL to the desired Amazon Best Sellers category page for Handmade products
    start_url = 'https://www.amazon.com/Best-Sellers-Handmade-Products/zgbs/handmade/ref=zg_bs_nav_handmade_0'
    driver.get(start_url)
    time.sleep(10)
    lazy_loading()  # To overcome lazy loading
    fetch_product_links_and_ranks()  # To fetch the links to products

# Creating a dictionary of the required columns
data_dic = {'product url': [],'ranking': [], 'brand': [], 'product name': [],
            'number of ratings': [], 'size': [], 'star rating': [], 'price(in dollar)': [], 'color': []}


# Creating a data frame with those columns
data = pd.DataFrame(data_dic)


# Assigning the scraped links and rankings to the columns 'product url' and 'ranking'
data['product url'] = product_links
data['ranking'] = ranking

for product in range(len(data)):
    product_url = data['product url'].iloc[product]
    product_content = extract_content(product_url)

    # brands
    extract_brand(product_content)

    # product_name
    extract_product_name(product_content)

    # price
    extract_price(product_content)

    # size
    extract_size(product_content)

    # star rating
    extract_star_rating(product_content)

    # number of ratings
    extract_num_of_ratings(product_content)

    # color
    extract_color(product_content)


# saving the resultant data frame as a csv file
data.to_csv('amazon_best_sellers_handmade_products.csv')





