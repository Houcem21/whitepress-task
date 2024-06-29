import pandas as pd
import requests
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib3
import socket

# SSL verification made things harder so I disabled it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fetch the content of each url page
def fetch_content(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    try:
        response = requests.get(url, timeout=10, verify=False)  # Set verify=False to disable SSL verification
        response.raise_for_status()
        return response.text
    except (requests.RequestException, socket.gaierror):
        return None
    except Exception:
        return None

# Extract the visible text from HTML content
def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)

# Filter visible text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# Detect the language of a webpage content
def detect_language(content):
    try:
        return detect(content)
    except LangDetectException:
        return "Unknown"


file_path = 'pages-whitepress.xlsx'
df = pd.read_excel(file_path, header=None)
df.columns = ['URL']
df['Language'] = ''

# Iterate through each URL and detect the language
for index, row in df.iterrows():
    url = row['URL']
    html_content = fetch_content(url)
    if html_content:
        text_content = extract_text(html_content)
        if text_content.strip():
            language = detect_language(text_content)
            if language == "Unknown":
                language = "not found"
        else:
            language = "not found"
        df.at[index, 'Language'] = language
    else:
        df.at[index, 'Language'] = "not found"

# Save the updated file
df.to_excel(file_path, index=False)
