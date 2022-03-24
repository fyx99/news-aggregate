
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



            
class Match:
    def __init__(self, tag_name, tag_attrs, tag_xpath="", tag_text="", tag_identifyable="TRUE"):
        self.tag_name = tag_name
        self.tag_attrs = tag_attrs
        self.tag_text = tag_text
        self.tag_xpath = tag_xpath
        self.tag_identifyable = tag_identifyable
    def __eq__(self, other):
        return self.tag_name == other.tag_name and self.tag_attrs == other.tag_attrs
    def __hash__(self):
        return hash(self.tag_name + self.tag_attrs)
    def __repr__(self) -> str:
        return f"{self.tag_name} {self.tag_attrs} {self.tag_xpath} {self.tag_identifyable}"
