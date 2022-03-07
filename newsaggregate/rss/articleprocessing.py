from bs4 import BeautifulSoup
from bs4.element import Tag

import json
from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.crud.article import get_articles_for_reprocessing
from newsaggregate.db.databaseinstance import DatabaseInterface
from random import randrange
from collections import defaultdict
import difflib
from urllib.parse import urlparse
from newsaggregate.db.postgresql import Database
from newsaggregate.storage.s3 import Datalake

def my_print(*args):
    argss = [str(arg)[:500] for arg in args]
    #print(*argss)

def longer(str1, str2):
    if len(str1) > len(str2):
        return str1
    return str2

class ArticleProcessingManager:
    def main():
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)
            articles_html = get_articles_for_reprocessing(di)
            ArticleProcessing.reprocess_article_unnecessary_tags(articles_html)

class ArticleProcessing:

    def xpath_soup(element):

        components = []
        child = element if element.name else element.parent
        for parent in child.parents:  # type: bs4.element.Tag
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name if 1 == len(siblings) else '%s[%d]' % (
                    child.name,
                    next(i for i, s in enumerate(siblings, 1) if s is child)
                    )
                )
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)
    
    def attrs_similar(x, y):
        #my_print(x,y )
        matches = {k: x[k] for k in x if k in y and x[k] == y[k]}
        if len(matches.keys()) == len(x.keys()):
            return True
        return False
    
    def identifyable(element, test_soup):
        if not hasattr(element, "name"):
            print("hm")
        element_count = len(test_soup.findAll(element.name, attrs=element.attrs))
        if element_count > 1:
            return False
        return True

    def identify_useless_parent(tag1, tag2):
        my_print("identify usedless")
        parent1 = tag1
        parent2 = tag2
        res_element = tag1
        while parent1 and parent2 and  parent1.parent and parent2.parent and difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio() > 0.8:
            my_print(f"Ratio: {difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio()}")
            my_print(f"Parent1: {parent1.name}, {parent1.attrs}")
            my_print(f"Parent2: {parent2.name}, {parent2.attrs}")

            if parent1.name == parent2.name:
                #my_print("hit")
                res_element = parent1
            parent1, parent2 = parent1.parent, parent2.parent

            while parent1 and parent2 and parent1.parent and parent2.parent and (parent1.name != parent2.name or not ArticleProcessing.attrs_similar(parent1.attrs, parent2.attrs)):
                if len(parent1.get_text()) > len(parent2.get_text()):
                    parent2 = parent2.parent
                    my_print("go parent2 up")
                else:
                    my_print("go parent1 up")
                    parent1 = parent1.parent
            # my_print(difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio())
            # my_print(len(parent1.parent.get_text()) , len(parent1.get_text()) , len(parent2.parent.get_text()) , len(parent2.get_text()))
        return res_element
    
    def get_children(element, only_tags=True):
        return [c for c in element.children if only_tags and type(c) == Tag]
        

    def identifiable_child(element, test_soup):
        identifiable_child = element
        while not ArticleProcessing.identifyable(identifiable_child, test_soup) and ArticleProcessing.get_children(identifiable_child):
            biggest_child = None
            for child in ArticleProcessing.get_children(identifiable_child):
                biggest_child = child if not biggest_child or (len(biggest_child.get_text()) < len(child.get_text()) and not child.name == "script") else biggest_child
            if not biggest_child:
                return identifiable_child
            identifiable_child = biggest_child
        return identifiable_child
        

    def compare_index(length):
        if length < 2:
            return False
        elif length == 2:
            return 0, 1
        index_a = randrange(length)
        index_b = randrange(length)
        while index_a == index_b:
            index_b = randrange(length)
        return index_a, index_b
    

    def compare_n_tags(soups, n=1):
        matches = []
        for _ in range(n):
            index_a, index_b = ArticleProcessing.compare_index(len(soups))
            matches.extend(ArticleProcessing.compare_two_tags(soups[index_a], soups[index_b], 0.8))
        return matches

    def element_saveable(element):
        return (element.name, json.dumps(element.attrs), ArticleProcessing.xpath_soup(element), element.get_text())
        

    def compare_two_tags(soup1, soup2, min_ratio=0.8):
        p_list1 = [p for p in soup1.findAll("p")]
        p_list2 = [p for p in soup2.findAll("p")]
        matches = []
        if difflib.SequenceMatcher(None, "".join([p.get_text() for p in p_list1]), "".join([p.get_text() for p in p_list2])).ratio() > 0.98:
            return []
        for t1 in p_list1:
            for t2 in p_list2:
                sq = difflib.SequenceMatcher(None, t1.get_text(), t2.get_text())
                if sq.ratio() > min_ratio:
                    useless_parent = ArticleProcessing.identify_useless_parent(t1, t2)
                    if useless_parent: 
                        useless_parent = ArticleProcessing.identifiable_child(useless_parent, soup2)
                        matches.append(ArticleProcessing.element_saveable(useless_parent))
        return matches

    def get_domain(url):
        return urlparse(url).netloc.replace("www.", "")


    def reprocess_article_unnecessary_tags(articles_sampled):
        # returns list of identifications for unnecessary tags


        #articles_sampled = [(e[13], e[1]) for e in data]
        articles_publisher = defaultdict(list)

        for article in articles_sampled:
            articles_publisher[ArticleProcessing.get_domain(article[1])].append(article[2])

        #new_list = articles_publisher.values()

        res = { publisher: ArticleProcessing.compare_n_tags([BeautifulSoup(e, "html.parser") for e in articles_list], len(articles_list) * 2) for publisher, articles_list in articles_publisher.items() if len(articles_list) > 1}
        my_print("here")

        my_print(res["dw.com"])
        #return res