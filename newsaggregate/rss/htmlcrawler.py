from collections import defaultdict
import traceback
from bs4 import BeautifulSoup
import requests
import json
from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.crud.article import save_article, set_article_status, get_unnecessary_text_pattern
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.rss.articleprocessing import ArticleProcessing
from newsaggregate.rss.articleutils import locate_article, Match
import time
import threading

class HTMLCrawler:

    patterns = defaultdict(list)

    def get_patterns(db):
        patterns_list = get_unnecessary_text_pattern(db)
        HTMLCrawler.patterns = defaultdict(list)
        [HTMLCrawler.patterns[pattern[0]].append(Match(pattern[1], json.loads(pattern[2]), "", pattern[3], pattern[4])) for pattern in patterns_list]
    
    def get_html(url):
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}, timeout=HTTP_TIMEOUT)
            if res.status_code == 200:
                return res.text, "ACTIVE"
            return res.text, "INACTIVE"
        except:
            return "", "INACTIVE"

    
    def find_tag_with_names(tag, names):
        if tag.name == "meta":
            for attr in tag.attrs.values():
                if attr in names:
                    return True
        return False
    
    def get_metadata(text):
        parser = "html.parser"
        soup = BeautifulSoup(text, parser)
    
        image_tags = soup.findAll(lambda t: HTMLCrawler.find_tag_with_names(t, ["twitter:image", "twitter:image:src", "og:image", "og:image:url"]))
        image_url = image_tags[0].attrs["content"] if len(image_tags) else ""
        
        amp_tag = soup.findAll("link", {"rel": "amphtml"})
        amp_url = amp_tag[0].attrs["href"] if len(amp_tag) else ""
        return {
            "image_url": image_url,
            "amp_url": amp_url
        }
    
    def parse_json_tags(json_scripts):
        json_parsed = []
        for script in json_scripts:
            try:
                json_parsed.append(json.loads(script.text))
            except Exception as e:
                print(e)
        return json_parsed

    
    def any_news_article(markups):
        for entry in markups:
            if '@type' in entry and entry['@type'] in ["Article", "ReportageNewsArticle", "NewsArticle"]:
                return entry
        return False
    
    def get_json_plus_metadata(soup):
        markups_flat = []
        try:
            markups = [json.loads("".join(e.contents)) for e in soup.findAll("script", {"type":"application/ld+json"})]
            for m in markups:
                if isinstance(m, dict):
                    markups_flat.append(m)
                    continue
                for n in m:
                    markups_flat.append(n)
        except json.decoder.JSONDecodeError as e:
            print("JSON DECODE ERROR")
        return HTMLCrawler.any_news_article(markups_flat)

    
    def clean_unnecessary(soup, url):
        for pattern in HTMLCrawler.patterns[ArticleProcessing.get_domain(url)]:
            if pattern.tag_identifyable == "TRUE":
                ps = soup.find_all(pattern.tag_name, attrs=pattern.tag_attrs)
                [p.clear() for p in ps]
            else:
                raise NotImplementedError

        return soup
        

    def parse_article(soup, url):
        article = locate_article(soup)
        article = HTMLCrawler.clean_unnecessary(article, url)
        if not article:
            raise Exception("No Article")

        article_text = " ".join([" ".join(p.get_text().split()) for p in article.findAll("p")])
        article_text = article_text.strip()
        article_h1 = soup.findAll("h1")
        article_title = article_h1[0].get_text() if len(article_h1) else ""
        article_title = article_title.strip()
        return article_text, article_title


    def run_single(db: DatabaseInterface, url: str, job_id: str):
        try:
            start = time.time()
            html, status = HTMLCrawler.get_html(url)
            get_html_time = time.time() - start
            if status == "INACTIVE":
                print(f"INACTIVE {url}")
                return set_article_status(db, job_id, status)
                
            parser = "html.parser"
            soup = BeautifulSoup(html, parser)
            markups = HTMLCrawler.get_json_plus_metadata(soup)
            meta = HTMLCrawler.get_metadata(html)

            _, img_status = HTMLCrawler.get_html(meta["image_url"])
            if img_status == "INACTIVE":
                print(f"INACTIVE IMAGE {url}")
                return set_article_status(db, job_id, status)

            article_text, article_title = HTMLCrawler.parse_article(soup, url)
            parse_html_time = time.time() - start - get_html_time
            save_article(db, job_id, markups, meta, html, article_text, article_title, status)
            save_article_time = time.time() - start - parse_html_time - get_html_time
            print(f"{threading.get_ident()}: get_html_time {get_html_time} parse_html_time {parse_html_time} save_article_time {save_article_time}", flush=True)
        except Exception as e:
            print("ERROR FOR " + url + " " + repr(e)) 
            print(traceback.format_exc())   
            
    def analyze(urls):
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            print(url)
            html = HTMLCrawler.get_html(url)
            markups = HTMLCrawler.get_json_plus_metadata(html)
            print(markups)
            meta = HTMLCrawler.get_metadata(html)
            print(meta)