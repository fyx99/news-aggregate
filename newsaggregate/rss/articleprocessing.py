from bs4 import BeautifulSoup
import json
from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.crud.article import get_articles_for_reprocessing
from newsaggregate.db.databaseinstance import DatabaseInterface
from random import randrange
from collections import defaultdict
import difflib

from newsaggregate.db.postgresql import Database
from newsaggregate.storage.s3 import Datalake

def print(*args):
    pass

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
    
    def attrs_similar(x, y):
        print(x,y )
        matches = {k: x[k] for k in x if k in y and x[k] == y[k]}
        if len(matches.keys()) == len(x.keys()):
            return True
        return False

    def identify_useless_parent(tag1, tag2):
        parent1 = tag1
        parent2 = tag2
        res = False

        while parent1.parent and parent2.parent and difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio() > 0.8:
            print(f"Ratio: {difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio()}")
            print(f"Parent1: {parent1.name}, {parent1.attrs}: {parent1.get_text()}")
            print(f"Parent2: {parent2.name}, {parent2.attrs}: {parent2.get_text()}")

            if parent1.name == parent2.name:
                print("hit")
                print(parent1.name, parent1)
                res = (parent1.name, json.dumps(parent1.attrs), longer(parent1.get_text(), parent2.get_text()))
                
            parent1 = parent1.parent
            parent2 = parent2.parent
            print("parent search")
            print(parent1.name, parent2.name)
            while parent1.name != parent2.name or not ArticleProcessing.attrs_similar(parent1.attrs, parent2.attrs):
                if len(parent1.get_text()) > len(parent2.get_text()):
                    parent2 = parent2.parent
                    print("go parent2 up")
                else:
                    print("go parent1 up")
                    parent1 = parent1.parent
            print(difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio())
        return res
        

    def compare_index(length):
        if length < 2:
            return False
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


    def compare_two_tags(soup1, soup2, min_ratio=0.8):
        p_list1 = [p for p in soup1.findAll("p")]
        p_list2 = [p for p in soup2.findAll("p")]
        matches = []
        for t1 in p_list1:
            for t2 in p_list2:
                sq = difflib.SequenceMatcher(None, t1.get_text(), t2.get_text())
                if sq.ratio() > min_ratio:
                    #(t1.get_text(), t2.get_text(), t1.parent, t2.parent.name))
                    matches.append(ArticleProcessing.identify_useless_parent(t1, t2))
        return matches

    def reprocess_article_unnecessary_tags(articles_sampled):
        # returns list of identifications for unnecessary tags
        print(articles_sampled)

        #articles_sampled = [(e[13], e[1]) for e in data]
        articles_publisher = defaultdict(list)

        for obj in articles_sampled:
            articles_publisher[obj[0]].append(obj[1])


        #new_list = articles_publisher.values()

        res = { publisher: ArticleProcessing.compare_n_tags([BeautifulSoup(e, "html.parser") for e in articles_list], len(articles_list) * 2) for publisher, articles_list in articles_publisher.items()}
        print(res)
        return res