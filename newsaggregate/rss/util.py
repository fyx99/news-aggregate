from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time

class Utils:
    def clean_link(url, feed_url):
        domain = Utils.get_domain(feed_url)
        url = domain + url if domain and url.startswith("/") else url
        url = "http://" + url if not url.startswith("http") else url
        return urljoin(url, urlparse(url).path)  
    def clean_text(text):
        parser = "html.parser"
        text = BeautifulSoup(text, parser).get_text()
        text = " ".join(text.split())
        text = re.sub('[^A-Za-z0-9äöüß.,!?#+-]+', ' ', text)
        text = text.strip()
        return text
    def clean_date(struct_date):
        return datetime.fromtimestamp(time.mktime(struct_date))
    def clean_date_string(datetime):
        return datetime.strftime("%Y-%m-%d %H:%M:%S")
    def clean_date_direct_string(struct_date):
        try:
            return datetime.fromtimestamp(time.mktime(struct_date)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_domain(url):
        return urlparse(url).netloc.replace("www.", "")