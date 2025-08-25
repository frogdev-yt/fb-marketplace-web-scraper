from selenium import webdriver
import os
import sys

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)
print(os.getcwd())

sloptions = webdriver.ChromeOptions()
sloptions.add_argument(f"--user-data-dir={script_dir}\\NewUserData")
sloptions.add_argument("--profile-directory=Default")
sloptions.page_load_strategy = "eager"
driver = webdriver.Chrome(options=sloptions)

driver.get("https://www.facebook.com/marketplace")


input("press enter in console when finished logging in\n")
driver.execute_cdp_cmd("Network.clearBrowserCache", {})
driver.quit()

email = input("enter your email address: ")
with open("email.txt","w") as f:
    f.write(email)