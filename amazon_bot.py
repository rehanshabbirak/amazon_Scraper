from bs4 import BeautifulSoup
import requests
import pandas
import time
from selenium import webdriver
import csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Amazon():
    def __init__(self,):
        self.chrome_options = Options()
        #self.chrome_options.add_argument('--headless')
        self.driver=webdriver.Chrome(options=self.chrome_options)
        self.driver.get("https://www.amazon.com/")
        time.sleep(3)
        self.driver.maximize_window()
    def Search_Keyword(self,keyword):
        try:
            search_box=self.driver.find_element(By.XPATH,"//input[@id='twotabsearchtextbox']")
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(4)
        except:
            search_box=self.driver.find_element(By.XPATH,"//input[@id='nav-bb-search']")
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(4)
    def Select_Price_Range(self,min_price_value,max_price_value):
        min_price=self.driver.find_element(By.XPATH,"//input[@id='low-price']")
        min_price.send_keys(min_price_value)
        time.sleep(0.5)
        max_price=self.driver.find_element(By.XPATH,"//input[@id='high-price']")
        max_price.send_keys(max_price_value)
        time.sleep(0.5)
        Go_button=self.driver.find_element(By.XPATH,"//input[@aria-labelledby='a-autoid-1-announce']")
        Go_button.click()
        time.sleep(5)
    def Parse_Data(self,):
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        first_products = soup.find_all('div', class_='s-card-container')

        data = []

        for first_product in first_products:
            try:
                product_link = first_product.find('a', class_='a-link-normal s-no-outline')
                if product_link:
                    base_url='https://www.amazon.com/'
                    product_link = base_url+product_link.get('href')
                else:
                    product_link = "Product link not found"

                product_name = first_product.find('span', class_='a-size-base-plus a-color-base a-text-normal')
                if product_name:
                    product_name = product_name.text.strip()
                else:
                    product_name = "Product name not found"

                rating = first_product.find('span', class_='a-size-base puis-normal-weight-text')
                rating2 = first_product.find('span', class_='a-size-base puis-bold-weight-text')
                if rating:
                    rating = rating.text.strip()
                elif rating2:
                    rating = rating2.text.strip()
                else:
                    rating = "Rating not found"

                total_reviews = first_product.find('span', class_='a-size-base s-underline-text')
                if total_reviews:
                    total_reviews = total_reviews.text.strip()
                else:
                    total_reviews = "Total reviews not found"

                #past_month_project = first_product.find('span', class_='a-size-base a-color-secondary')
                #if past_month_project:
                 #   past_month_project = past_month_project.text.strip()
                #else:
                 #   past_month_project = "Past month project not found"

                price = first_product.find('span', class_='a-offscreen')
                if price:
                    price = price.text.strip()
                else:
                    price = "Price not found"

                data.append([product_name, rating, total_reviews,  price, product_link])

            except Exception as e:
                print("Error parsing data:", str(e))

        return data if data else [] 
    def Go_To_Next_Pages(self):
        try:
            next_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Next']"))
            )
            if next_button:
                next_button.click()
                time.sleep(4)
                self.Parse_Data()
            else:
                print("No more pages available.")
        except NoSuchElementException as e:
            print("Error navigating to the next page:", str(e))
            print("No more pages available.")
    def rating_function(self,rating):
            ratings_section = self.driver.find_element(By.ID, 'reviewsRefinements')
            rating_elements = ratings_section.find_element(By.XPATH, f".//section[@aria-label='{rating} Stars & Up']")
            rating_elements.click()        

    def export_to_csv(self, data, filename):
        try:
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write header row
                header_row = ["Product Name", "Rating", "Total Reviews",  "Price", "Product Link"]
                csvwriter.writerow(header_row)

                # Write data rows
                for row in data:
                    csvwriter.writerow(row)

            print(f'Data has been successfully exported to {filename}')
        except Exception as e:
            print(f'Error exporting data to {filename}: {str(e)}')           
        
am = Amazon()
product_name = input("Enter the product name: ")
am.Search_Keyword(product_name)
price_range=input("do you want to enter the price range?(yes/no)").strip().lower()
if price_range =="yes":
    minimum_value=int(input("enter the minimum value"))
    maximum_value=int(input("enter the maximum value"))
    am.Select_Price_Range(minimum_value,maximum_value)
else:
    pass
rating=input("do you want to filter data on the basis of rating(yes/no)").strip().lower()
if rating=="yes":
    rating_range=int(input("please select the rating up_to(1,2,3,4)"))
    am.rating_function(rating_range)
else:
    pass    
next_page = input("Do you want to navigate more than one page? (yes/no): ").strip().lower()

if next_page == "yes":
    num_pages_to_parse = int(input("Enter the number of pages to navigate (0 for only the first page): "))
    all_data = []
    data = am.Parse_Data()
    all_data.extend(data)
    i=0
    try:
        for _ in range(num_pages_to_parse):
            i=i+1
            print(f"The {i} page is parsing ")
            am.Go_To_Next_Pages()
            data = am.Parse_Data()
            all_data.extend(data)
        am.export_to_csv(all_data, f'{product_name}.csv')
    except:
        print("No more pages")
else:
    data = am.Parse_Data()
    if data:
        for item in data:
            print("Product Name:", item[0])
            print("Rating:", item[1])
            print("Total Reviews:", item[2])
            print("Price:", item[3])
            print("Product Link:", item[4])
            print("-" * 50)
        am.export_to_csv(data, f'{product_name}.csv')       
    else:
        print("No data found on the current page.")