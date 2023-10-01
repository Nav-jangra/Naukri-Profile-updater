#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""

import random
import re
import os
import io
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from PyPDF2 import PdfReader, PdfWriter
from string import ascii_uppercase, digits
from random import choice, randint
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from webdriver_manager.chrome import ChromeDriverManager as CM


# Add folder Path of your resume
originalResumePath = "MY_resumeaa_path.pdf"
# Add Path where modified resume should be saved
modifiedResumePath = "MY_edited_resume_path.pdf"

# Update your naukri username and password here before running
username = "MY_USER_NAME"
password = "MY_PASSWOED"
mob = "MY_NUMBER"  # Type your mobile number here

# False if you dont want to add Random HIDDEN chars to your resume
updatePDF = True

# ----- No other changes required -----

# Set login URL
NaukriURL = "https://www.naukri.com/nlogin/login"

logging.basicConfig(
    level=logging.INFO, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ['WDM_LOCAL'] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    exc_type, exc_obj, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID" : By.ID,
        "NAME" : By.NAME,
        "XPATH" : By.XPATH,
        "TAG" : By.TAG_NAME,
        "CLASS" : By.CLASS_NAME,
        "CSS" : By.CSS_SELECTOR,
        "LINKTEXT" : By.LINK_TEXT
    }
    return map[locatorType]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:
        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag))

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for i in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg('Exception when WaitTillElementPresent : %s' %e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))


def LoadNaukri(headless):
    """Open Chrome to load Naukri.com"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")  # ("--kiosk") for MAC
    options.add_argument("--disable-popups")
    options.add_argument("--disable-gpu")
    if headless:
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("headless")

    # updated to use ChromeDriverManager to match correct chromedriver automatically
    driver = None
    try:
        driver = webdriver.Chrome(executable_path=CM().install(), options=options)
    except:
        driver = webdriver.Chrome(options=options)
    log_msg("Google Chrome Launched!")

    driver.implicitly_wait(3)
    driver.get(NaukriURL)
    return driver


def naukriLogin(headless = False):
    """ Open Chrome browser and Login to Naukri.com"""
    status = False
    driver = None

    try:
        driver = LoadNaukri(headless)

        if "naukri" in driver.title.lower():
            log_msg("Website Loaded Successfully.")

        emailFieldElement = None
        if is_element_present(driver, By.ID, "emailTxt"):
            emailFieldElement = GetElement(driver, "emailTxt", locator="ID")
            time.sleep(1)
            passFieldElement = GetElement(driver, "pwd1", locator="ID")
            time.sleep(1)
            loginXpath = "//*[@type='submit' and @value='Login']"
            loginButton = GetElement(driver, loginXpath, locator="XPATH")

        elif is_element_present(driver, By.ID, "usernameField"):
            emailFieldElement = GetElement(driver, "usernameField", locator="ID")
            time.sleep(1)
            passFieldElement = GetElement(driver, "passwordField", locator="ID")
            time.sleep(1)
            loginXpath = '//*[@type="submit"]'
            loginButton = GetElement(driver, loginXpath, locator="XPATH")

        else:
            log_msg("None of the elements found to login.")

        if emailFieldElement is not None:
            emailFieldElement.clear()
            emailFieldElement.send_keys(username)
            time.sleep(1)
            passFieldElement.clear()
            passFieldElement.send_keys(password)
            time.sleep(1)
            loginButton.send_keys(Keys.ENTER)
            time.sleep(1)

            # Added click to Skip button
            #print("Checking Skip button")
            # skipAdXpath = "//*[text() = 'SKIP AND CONTINUE']"
            # if WaitTillElementPresent(driver, skipAdXpath, locator="XPATH", timeout=10):
            #     GetElement(driver, skipAdXpath, locator="XPATH").click()

            # CheckPoint to verify login
            # if WaitTillElementPresent(driver, "search-jobs", locator="ID", timeout=40):
            #     CheckPoint = GetElement(driver, "search-jobs", locator="ID")
            #     if CheckPoint:
            #         log_msg("Naukri Login Successful")
            #         status = True
            #         return (status, driver)
            #     else:
            #         log_msg("Unknown Login Error")
            #         return (status, driver)
            # else:
            #     log_msg("Unknown Login Error")
            return (True, driver)

    except Exception as e:
        catch(e)
    return (True, driver)


def UpdateProfile(driver):
    try:
        mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
        profeditXpath = "//a[contains(text(), 'UPDATE PROFILE')] | //a[contains(text(), ' Snapshot')] | //a[contains(@href, 'profile') and contains(@href, 'home')]"
        saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
        editXpath = "//em[text()='Edit']"

        WaitTillElementPresent(driver, profeditXpath, "XPATH", 20)
        profElement = GetElement(driver, profeditXpath, locator="XPATH")
        profElement.click()
        driver.implicitly_wait(2)

        WaitTillElementPresent(driver, editXpath + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, editXpath):
            editElement = GetElement(driver, editXpath, locator="XPATH")
            editElement.click()

            WaitTillElementPresent(driver, mobXpath, "XPATH", 20)
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            mobFieldElement.clear()
            mobFieldElement.send_keys(mob)
            driver.implicitly_wait(2)

            saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            saveFieldElement.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)

            WaitTillElementPresent(driver, "//*[text()='today']", "XPATH", 10)
            if is_element_present(driver, By.XPATH, "//*[text()='today']"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        elif is_element_present(driver, By.XPATH, saveXpath):
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            mobFieldElement.clear()
            mobFieldElement.send_keys(mob)
            driver.implicitly_wait(2)

            saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            saveFieldElement.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)

            WaitTillElementPresent(driver, "confirmMessage", locator="ID", timeout=10)
            if is_element_present(driver, By.ID, "confirmMessage"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        time.sleep(5)

    except Exception as e:
        catch(e)


def UpdateResume():
    try:
        # random text with with random location and size
        txt = randomText()
        xloc = random.randint(700, 1000)  # this ensures that text is 'out of page'
        fsize = random.randint(1, 10)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", fsize)
        can.drawString(xloc, 100, "lon")
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(originalResumePath, "rb"))
        pagecount = len(existing_pdf.pages)
        log_msg("Found %s pages in PDF" % pagecount)

        output = PdfWriter()
        # Merging new pdf with last page of my existing pdf
        # Updated to get last page for pdf files with varying page count
        for pageNum in range(pagecount - 1):
            output.addPage(existing_pdf.getPage(pageNum))

        page = existing_pdf.pages[pagecount - 1]
        page.merge_page(new_pdf.pages[0]) 
        output.add_page(page)
        # save the new resume file
        with open(modifiedResumePath, "wb") as outputStream:
            output.write(outputStream)
        log_msg("Saved modified PDF : %s" % modifiedResumePath)
        return os.path.abspath(modifiedResumePath)
    except Exception as e:
        catch(e)
    return os.path.abspath(originalResumePath)


def UploadResume(driver, resumePath):
    try:
        attachCVID = "attachCV"
        CheckPointXpath = "//*[contains(@class, 'updateOn')]"
        saveXpath = "//button[@type='button']"

        driver.get("https://www.naukri.com/mnjuser/profile")
        WaitTillElementPresent(driver, attachCVID, locator="ID", timeout=10)
        AttachElement = GetElement(driver, attachCVID, locator="ID")
        AttachElement.send_keys(resumePath)

        if WaitTillElementPresent(driver, saveXpath, locator="ID", timeout=5):
            saveElement = GetElement(driver, saveXpath, locator="XPATH")
            saveElement.click()

        WaitTillElementPresent(driver, CheckPointXpath, locator="XPATH", timeout=30)
        CheckPoint = GetElement(driver, CheckPointXpath, locator="XPATH")
        if CheckPoint:
            LastUpdatedDate = CheckPoint.text
            todaysDate1 = datetime.today().strftime("%b %d, %Y")
            todaysDate2 = datetime.today().strftime("%b %#d, %Y")
            if todaysDate1 in LastUpdatedDate or todaysDate2 in LastUpdatedDate:
                log_msg(
                    "Resume Document Upload Successful. Last Updated date = %s"
                    % LastUpdatedDate
                )
            else:
                log_msg(
                    "Resume Document Upload failed. Last Updated date = %s"
                    % LastUpdatedDate
                )
        else:
            log_msg("Resume Document Upload failed. Last Updated date not found.")

    except Exception as e:
        catch(e)
    time.sleep(2)


def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin()
        if status:
            UpdateProfile(driver)
            if os.path.exists(originalResumePath):
                if updatePDF:
                    resumePath = UpdateResume()
                    UploadResume(driver, resumePath)
                else:
                    UploadResume(driver, originalResumePath)
            else:
                log_msg("Resume not found at %s " % originalResumePath)
    except Exception as e:
        catch(e)

    finally:
        tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")


if __name__ == "__main__":
    main()
