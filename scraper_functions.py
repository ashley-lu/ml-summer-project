import pandas as pd
import requests
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sqlite3

"""
Gets all of the poem links from a single page on Poetry Foundation. Continues to loop until all of the poem links can be
found on the page and there are no exceptions.

Input: page number
Output: list of poem links for a single page
"""
def get_links(page):
    poem_links = []
    for j in range(0, 5):
        try:
            driver.get("https://www.poetryfoundation.org/poems/browse#page={}".format(page))
            xpath = "//h2[@class='c-hdgSans c-hdgSans_2']/a[contains(@href, 'poetryfoundation.org')]"
            # wait until all poem links are located
            WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            links = driver.find_elements_by_xpath(xpath)
            # scroll to the last element found so the bottom elements won't be skipped
            driver.execute_script('arguments[0].scrollIntoView();', links[-1])
            # wait again until all poem links are located
            WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            links = driver.find_elements_by_xpath(xpath)
            for link in links:
                try:
                    href = link.get_attribute("href")
                    poem_links.append(href)
                except Exception:
                    continue
            break
        except Exception:
            # if elements could not be located, the page is refreshed
            driver.refresh()
    return poem_links

"""
Gets the title of the poem and returns it, unless no title can be found, in which None is returned.

Input: poem link
Output: the poem title if it could be located, None otherwise
"""
def get_poem_title(page):
    driver.get(page)
    try:
        title = driver.find_element_by_xpath("//h1[@class='c-hdgSans c-hdgSans_2 c-mix-hdgSans_inline']").text
        return title
    except Exception:
        try:
            # alternate xpath for titles
            title = driver.find_element_by_xpath("//span[@class='c-hdgSans c-hdgSans_7']").text
            return title
        except Exception:
            return None
    return None

"""
Gets the author of the poem and returns it, unless no author can be found, in which None is returned.

Input: poem link
Output: the poem author if it could be located, None otherwise
"""
def get_poem_author(page):
    driver.get(page)
    try:
        author = driver.find_element_by_xpath("//span[@class='c-txt c-txt_attribution']").text
        return author
    except Exception:
        return None

"""
Gets the text of the poem and returns it, unless no text can be found, in which an empty string is returned.

Input: poem link
Output: the poem text if it could be located, an empty string otherwise
"""
def get_poem_text(page):
    driver.get(page)
    try:
        temp_text = driver.find_elements_by_xpath("//div[@style='text-indent: -1em; padding-left: 1em;']")
    except Exception:
        temp_text = driver.find_elements_by_xpath("//div[@class='o-poem isActive']/p")
    text_string = ""
    for text in temp_text:
        if text != temp_text[len(temp_text) - 1]:
            text_string += text.text + "\n"
        else:
            text_string += text.text
    return text_string

"""
Gets the tags of the poem and returns them, unless no tags can be found, in which None is returned.

Input: poem link
Output: the poem tags if they could be located, None otherwise
"""
def get_poem_tags(page):
    driver.get(page)
    try:
        # clicking button to open window containing tabs
        button = driver.find_element_by_xpath("//button[@class='c-btn c-btn_pullTab']")
        button.click()
    except Exception:
        return None
    try:
        # wait until all tags are located
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='c-index-bd']/ul/li/a[@class='c-btn c-btn_tag']")))
        temp_tags = driver.find_elements_by_xpath("//div[@class='c-index-bd']/ul/li/a[@class='c-btn c-btn_tag']")
        # scroll to the last element found so the bottom elements won't be skipped
        driver.execute_script('arguments[0].scrollIntoView();', temp_tags[-1])
        # wait again until all tags are located
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='c-index-bd']/ul/li/a[@class='c-btn c-btn_tag']")))
        temp_tags = driver.find_elements_by_xpath("//div[@class='c-index-bd']/ul/li/a[@class='c-btn c-btn_tag']")
        tag_string = ""
        for i in range(len(temp_tags)):
            # some tags cannot be read and end up as empty strings, so those are filtered out using regex
            if re.search(r'[A-Za-z]', temp_tags[i].text) == None:
                continue
            # do not add comma to string if next element is empty string
            if temp_tags[i] != temp_tags[len(temp_tags) - 1] and temp_tags[i + 1] == "":
                tag_string += temp_tags[i].text
                continue
            if temp_tags[i] != temp_tags[len(temp_tags) - 1]:
                tag_string += temp_tags[i].text + ", "
            else:
                tag_string += temp_tags[i].text
    except Exception:
        tag_string = None
    return tag_string
