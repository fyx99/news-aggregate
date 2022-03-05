from bs4 import BeautifulSoup
import requests
import json
from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.crud.article import save_article, set_article_status
from newsaggregate.db.databaseinstance import DatabaseInterface

class HTMLCrawler:
    
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

    
    def locate_article(soup):
        #exactly one article
        article_hits = soup.findAll("article")
        if len(article_hits) == 1:
            return article_hits[0]
        #exactly one article in content
        content = soup.find("div", {"class": "content"})
        content_article_hits = content.findAll("article") if content else []
        if len(content_article_hits) == 1:
            return content_article_hits[0]
        # #parent of h1
        # content = soup.find("h1")

        def most_text_paragraphs_in_articles(articles):
            articles_char_len = [len(" ".join([p.get_text() for p in soup.findAll("p")])) for soup in articles]
            if not len(articles_char_len):
                return None, -1
            index = articles_char_len.index(max(articles_char_len)) 
            return articles[index], articles_char_len[index]
        #only take longest text 
        max_article, num_chars = most_text_paragraphs_in_articles(article_hits)
        if len(article_hits) > 1 and num_chars > 300:
            return max_article

        #content
        if content:
            return content
        #main
        main = soup.find("main")
        if main:
            return main

        #body
        body = soup.find("body")
        if body:
            return body
        return soup
    

    def parse_article(soup):
        article = HTMLCrawler.locate_article(soup)

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
            html, status = HTMLCrawler.get_html(url)
            if status == "INACTIVE":
                set_article_status(db, job_id, status)
                raise Exception("INACTIVE")
            parser = "html.parser"
            soup = BeautifulSoup(html, parser)
            markups = HTMLCrawler.get_json_plus_metadata(soup)
            meta = HTMLCrawler.get_metadata(html)
            article_text, article_title = HTMLCrawler.parse_article(soup)
            save_article(db, job_id, markups, meta, html, article_text, article_title, status)
        except Exception as e:
            print("ERROR FOR " + url + " " + repr(e))    
            
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