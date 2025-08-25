import selenium
from selenium import webdriver
import selenium.common
import selenium.types
import selenium.webdriver
import selenium.webdriver.common
from selenium.webdriver.common.by import By
import selenium.webdriver.remote
import selenium.webdriver.remote.webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from tkinter import *
from tkinter import ttk
import time
import os
import sys
import re
import smtplib
from email.message import EmailMessage
import traceback


# load search settings, keyed by search terms
searchsettings = {
    "gsx r": 
    [
        {
            #"modelname": ["gsxr","gsx-r","gsx r"], # deprecated
            "modelpattern": r"gsx.{0,6}r",
            "cc": [600],
            "pricemin": 1000,
            "pricemax": 5500
            # km req later
        },
        {
            "modelpattern": r"gsx.{0,6}r",
            "cc": [750],
            "pricemin": 1000,
            "pricemax": 6000
        },
        {
            "modelpattern": r"gsx.{0,6}r",
            "cc": [1000],
            "pricemin": 1000,
            "pricemax": 7000
        },
    ],
    "kawasaki ninja": 
    [
        {
            "modelpattern": "ninja",
            "cc": [300],
            "pricemin": 1000,
            "pricemax": 2000
        },
        {
            "modelpattern": "ninja",
            "cc": [400,650],
            "pricemin": 1000,
            "pricemax": 5000
        }
    ],
    "cbr":
    [
        {
            "modelpattern": r"cbr",
            "cc": [500],
            "pricemin": 1000,
            "pricemax": 4500
        },
        {
            "modelpattern": r"cbr",
            "cc": [600],
            "pricemin": 1000,
            "pricemax": 5500
        },
        {
            "modelpattern": r"cbr",
            "cc": [1000],
            "pricemin": 1000,
            "pricemax": 6000
        },
    ],
    "yzf":
    [
        {
            "modelpattern": r"r3(?!\d)",
            "cc": [300],
            "pricemin": 1000,
            "pricemax": 4000
        },
        {
            "modelpattern": r"r6(?!\d)",
            "cc": [600],
            "pricemin": 1000,
            "pricemax": 6000
        },
        {
            "modelpattern": r"r1(?!\d)",
            "cc": [1000],
            "pricemin": 1000,
            "pricemax": 6000
        },
    ]
}

# set working directory
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)
print(os.getcwd())

# make data folder if it doesnt exist
os.makedirs("Data",exist_ok=True)

with open("email.txt") as f:
    address = f.read()

# wrongmodels = []
# rightmodels = {}
# steals = {}

def sendemail(contents):
    msg = EmailMessage()
    msg["Subject"] = "Awesome sloppy facebook marketplace steal found"
    msg["From"] = "slopper@poopfart.com"
    msg["To"] = address
    msg.set_content(contents)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("cameronjplayfair@gmail.com", "kuur frtk kzem kfel")
        server.send_message(msg)


def checkdesc(title: str, link: str): # return whether it has desired model name in desc, and cc (look for 600,650,750,700 wtv)
    correctmodel = False
    cc = 0
    possiblems = []

    # by default, chooses most lenient price guidelines in case cc is missed when a steal is actually there
    chosenm = max(searchsettings[currentsearch], key=lambda x: x["pricemax"])
    
    # switch to check tab 
    try:
        print("try to switch to the check window nyeh heh heh")
        # driver.switch_to.window(checkwindow)
        driver.switch_to.window(driver.window_handles[1])
        print("switched to check window, opening link in 1 second")
        time.sleep(1)
        driver.get(link)
        print("opened link")
    except Exception as e:
        traceback.print_exc()
        print("somehow it has a fucking issue with the session id even though there is NO issue to be had I will rolest this program man I swear")
        print(f"loops: {loops}")
        input("paused:")

    # wait until collection of marketplace items loaded
    # to find right panel, look for message box after the depth that every one of this page has in common (has a very specific xpath)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]")) # check for presence of common element ("Collection of Marketplace items")
    )
    # try searching for map text or something
    # or search "seller information" with xpath
    # then take parent
    # search for something at a low level that is universal, like a little snippet of xpath or a piece of text, then work up to right panel
    try:
        # right panel as parent of message box
        # hopefully the seller information box has the same structure on every page
        # it does not
        # rightpanel = driver.find_element(By.XPATH, ".//*[contains(text(),'Seller information')]/../../../../../../../../../../../../../../../..")
        collection = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]")
    except Exception as e:
        print("Error could not find right panel: " + str(e))
        input("enter to close:")
        driver.quit()

    try:
        print("pressing see more button")
        seemorebutton = collection.find_element(By.XPATH,".//span[text()='See more']")
        seemorebutton.click()
    except Exception:
        print("short description")

    
    # might not split correctly if theres weird stuff in right panel but oh well
    desc = collection.text.split("Message")[1].split("Seller information")[0]
    print(desc)
    for m in searchsettings[currentsearch]:
        t = m["modelpattern"]
        print(f"checking title for {t}")
        if re.search(t, title, re.IGNORECASE):
            print("model found in title")
            if m not in possiblems:
                possiblems.append(m)
            correctmodel = True

        print(f"checking desc for {t}")
        if re.search(t, desc, re.IGNORECASE):
            print("model found in desc")
            if m not in possiblems:
                possiblems.append(m)
            correctmodel = True
    
    if not correctmodel:
        print("model name not found anywhere, closing window")
        # driver.close()
        # driver.switch_to.window(ogwindow)
        driver.switch_to.window(driver.window_handles[0])
        return [correctmodel,cc,0]

    # model is correct, time to find cc
    print("correct model found, finding cc")

    # check cc hard coded in mobile vehicle desc first

    print(f"chosen m (most lenient price) is {chosenm}")
    for m in possiblems:
        for c in m["cc"]:
            print(f"checking if {c} cc")
            pattern = r"(?<!\d)" + str(c) + r"(?!\d)" # checks for lone number of cc
            if re.search(pattern, title):
                cc = c
                chosenm = m
                print("cc found in title")
            elif re.search(pattern, desc):
                cc = c
                chosenm = m
                print("cc found in desc")
            else:
                if currentsearch == "yzf":
                    cc = m["cc"][0]
                    print(f"cc {cc} yoinked because its a yzf")

    mindex = searchsettings[currentsearch].index(chosenm)
    print(f"returning {correctmodel}, {cc}, {mindex}")
    # driver.close()
    # driver.switch_to.window(ogwindow)
    driver.switch_to.window(driver.window_handles[0])
    return [correctmodel,cc,mindex] # returns index of search setting that has matching cc
    

def MeetsPrice(price: int,chosenindex: int) -> bool:
    if price != 1234 and price <= searchsettings[currentsearch][chosenindex]["pricemax"] and price >= searchsettings[currentsearch][chosenindex]["pricemin"]:
        return True
    else:
        return False

def checklistings(sloppers : list[selenium.webdriver.remote.webelement.WebElement]):
    # should be scrolled to the top right now
    initialscrollheight = driver.execute_script("return window.scrollY")

    for l in sloppers:

        print(f"Trying listing card {sloppers.index(l)}")
        scrolledtotop = False
        for i in range(scrolls*5): # scrolls to be performed from top, x5 because thingle scrolls in increments of 1000 instead of 5000
            try:
                info = l.find_element(By.XPATH,".//a/div/div[2]") # doesnt always follow the structure div/a/div/div[2]
                print(info.get_attribute("class"))
                elements = info.find_elements(By.XPATH,"div")
                print("listing found")
                break
            except Exception as e:
                # if not found, scroll from top
                if not scrolledtotop:
                    driver.execute_script(f"window.scrollTo(0,{initialscrollheight})")
                    scrolledtotop = True
                
                print("haven't reached element yet")
                print(sloppers.index(l))
                driver.execute_script("window.scrollBy(0, 1000);") # 1000 instead of 5000 cause somehow its missing some?
        else:
            print("reached end of scrolling and still havent found listing, doesnt exist prolly")
            input("paused, enter to continue:")
            # scroll back to start of listing check
            continue

        price = elements[0].text
        print(f"price: {price}")
        title = elements[1].text
        print(f"title: {title}")
        if len(elements) > 3:
            km = elements[3].text
            print(f"km: {km}")
        else:
            print("no kmage found")
            km = ""
        
        link = l.find_element(By.XPATH,".//a").get_attribute("href")
        print(f"link: {link}")
        id = link.split("https://www.facebook.com/marketplace/item/")[1].split("/")[0]
        print(f"id: {id}")

        if price.lower().find("free") == -1:
            # is not free
            priceint = int(re.sub("\D","",price.split("$")[1]))
        else:
            priceint = 0
        
        print(f"priceint: {priceint}")
        if km != "":
            if len(km.split("K")) > 1:
                kmint = int(float(km.split("K")[0])*1000)
            else:
                kmint = re.sub("\D","",km)
        else:
            kmint = 0

        print(f"listing:")
        print(f"{title}, {priceint}, {kmint} id={id}")

        details = {
            "title": title,
            "price": priceint,
            "cc": 0,
            "km": kmint,
            "link": link
        }

        if id in wrongmodels:
            print("bike already checked, wrong model\n")
        elif id in steals:
            print("bike already on steals list\n")
        elif id in rightmodels:
            # even if known, still check if meets reqs in case price has changed
            laxm = max(searchsettings[currentsearch], key=lambda x: x["pricemax"])
            index = searchsettings[currentsearch].index(laxm)
            print("known listing")
            cc = rightmodels[id]["cc"]
            print(f"known cc: {cc}")
            for m in searchsettings[currentsearch]:
                for c in m["cc"]:
                    if c == cc:
                        index = searchsettings[currentsearch].index(m)
                        print(f"price check index: {index}")
            if cc in searchsettings[currentsearch][index]["cc"] and MeetsPrice(priceint,index):
                print("steal found, notifying\n")
                # notify brotify
                sendemail(f"{title}\n{link}")
                steals[id] = details

                # insta write steals
                with open(f"Data/steals-{k}.json","w") as file:
                    json.dump(steals,file)
                
            else:
                print("listing does not meet reqs\n")
        else:
            # unknown bikeicle
            checked = checkdesc(title, link)
            if checked[0]: # checked[0] is correctmodel
                print("correct model spotted")
                details["cc"] = checked[1]
                rightmodels[id] = details

                # insta write right models
                with open(f"Data/rightmodels-{k}.json","w") as file:
                    json.dump(rightmodels,file)
                
                if checked[1] in searchsettings[currentsearch][checked[2]]["cc"] and MeetsPrice(priceint,checked[2]):
                    print("steal found, notifying\n")
                    # notify brotify
                    sendemail(f"{title}\n{link}")
                    steals[id] = details

                    # insta write steals
                    with open(f"Data/steals-{k}.json","w") as file:
                        json.dump(steals,file)

                else:
                    print("listing does not meet reqs\n")
            else:
                print("wrong model\n")
                wrongmodels.append(id)

                # insta write wrong models
                with open(f"Data/wrongmodels-{k}.json","w") as file:
                    json.dump(wrongmodels,file)

loops = 0
while True:
    sloptions = webdriver.ChromeOptions()
    sloptions.add_argument(f"--user-data-dir={script_dir}\\NewUserData")
    sloptions.add_argument("--profile-directory=Default")
    
    # headless mode test
    # sloptions.add_argument("--headless")
    # sloptions.add_argument("--disable-gpu")
    
    sloptions.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=sloptions)

    # boot up the iframe
    driver.execute_script(
    """
    let iframe = document.createElement('iframe');
    iframe.src = 'https://some-url.com';
    iframe.id = 'myFrame';
    document.body.appendChild(iframe);
    """
    )

    # repeat this every however often for whatever searches you need - split the waiting time up into the different searches you need
    for k in searchsettings.keys():
        
        # load known stuff from file
        try:
            with open(f"Data/wrongmodels-{k}.json","r") as file:
                wrongmodels = json.load(file)
        except FileNotFoundError:
            print("no wrong model list found")
            wrongmodels = []

        try:
            with open(f"Data/rightmodels-{k}.json","r") as file:
                rightmodels = json.load(file)
        except FileNotFoundError:
            print("no right model list found")
            rightmodels = {}

        try:
            with open(f"Data/steals-{k}.json","r") as file:
                steals = json.load(file)
        except FileNotFoundError:
            print("no steals list found")
            steals = {}

        print("loaded data")
        print(f"{k} steals: {steals}")
        print(f"{k} right models: {rightmodels}")
        print(f"{k} wrong models: {wrongmodels}")

        currentsearch = k
        try:
            driver.get(f"https://www.facebook.com/marketplace/melbourne/search/?query={currentsearch}&radius=250") # this should be run with the chosen settings
            
            # wait until listings loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div/div[2]"))
            )
            listingschecked = 0
            reachedoutersearch = False

            scrolls = 0
            # move desired scrolls definition to be up with search settings, set this as setting when launching program
            desiredscrolls = 5

            divscount = len(driver.find_elements(By.TAG_NAME, "div"))
            while not reachedoutersearch: # and scrolls < desiredscrolls - scrolls until reaches secondary results OR reaches desired scrolls threshold (outside your search yadda yadda)
                try:
                    scrolls += 1
                    driver.execute_script("window.scrollBy(0, 5000);")
                    WebDriverWait(driver, 10).until(
                            lambda d: len(driver.find_elements(By.TAG_NAME, "div")) > divscount
                        )
                    divscount = len(driver.find_elements(By.TAG_NAME, "div"))
                    print(f"new divs count {divscount}")
                    secondarylistings = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div[2]/div[2]")
                    reachedoutersearch = True
                except:
                    print("haven't reached secondary results yet")
                    print(f"scrolled {scrolls} times")

            outersearchheight = driver.execute_script("return window.scrollY")

            # reached outer search, search inner first
            driver.execute_script("window.scrollTo(0,0)")
            listingcontainer = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div/div[2]')
            listings = listingcontainer.find_elements(By.XPATH,"div/div/div/span/div/div/div")
            # return a deeper part of the grid card that only exists on real listings not empty boxes
            # this avoids returning empty boxes in the listings grid, will only return actual listings, not ads or nun
            checklistings(listings)


            # now search outer for remaining scrolls out of x desired scrolls
            if scrolls < desiredscrolls:
                
                # set scrolls to remaining scrolls to be carried out
                scrolls = desiredscrolls - scrolls
                divscount = len(driver.find_elements(By.TAG_NAME, "div"))
                print(f"total divs count: {divscount}")
                for i in range(scrolls):
                    driver.execute_script("window.scrollBy(0, 5000);")
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda d: len(driver.find_elements(By.TAG_NAME, "div")) > divscount
                        )
                        divscount = len(driver.find_elements(By.TAG_NAME, "div"))
                        print(f"new divs count {divscount}")
                    except:
                        print("no new divs discovered in 10s wait")
                
                driver.execute_script(f"window.scrollTo(0,{outersearchheight})")
                listingcontainer = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div[2]/div[2]")
                listings = listingcontainer.find_elements(By.XPATH,"div/div/div/span/div/div/div")
                checklistings(listings)

            
            print(f"{k} steals: {steals}")
            print(f"{k} right models: {rightmodels}")
            print(f"{k} wrong models: {wrongmodels}")

            with open(f"Data/steals-{k}.json","w") as file:
                json.dump(steals,file)
            with open(f"Data/rightmodels-{k}.json","w") as file:
                json.dump(rightmodels,file)
            with open(f"Data/wrongmodels-{k}.json","w") as file:
                json.dump(wrongmodels,file)
                
        except Exception as e:
            print(f"Browser closing, exception type: {type(e)}")
            print(f"traceback: {traceback.print_exc()}")
            input("enter to start close browser\n")
            driver.quit()


    loops += 1
    print("script finished")
    driver.execute_cdp_cmd("Network.clearBrowserCache", {})
    driver.quit()

    print("waiting to run it back")
    time.sleep(10) # wait x minutes, do the whole thing again


# upon launching file, chosen search settings are read from file
#with open("settings.json", encoding="utf-8") as f:d
#    read_data = f.read()

# gui to change settings is launched
