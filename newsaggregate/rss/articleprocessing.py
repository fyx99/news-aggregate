from bs4 import BeautifulSoup
import json
from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.databaseinstance import DatabaseInterface
from random import randrange
from collections import defaultdict
import difflib

class ArticleProcessing:
    


    def identify_useless_parent(tag1, tag2):
        parent1 = tag1
        parent2 = tag2

        #while parent.parent and len(parent.get_text()) * 0.9 <= len(tag.get_text()):
        
        while parent1.parent and parent2.parent and difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio() > 0.8:
            print(difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio())
            print(parent1.name, parent1.attrs)
            print(parent2.name, parent2.attrs)
            print(parent1.get_text())
            print(parent2.get_text())
            if parent1.name == parent2.name:
                print("hit")
                print(parent1.name, parent1)
                return (parent1.name, parent1.attrs)
            parent1 = parent1.parent
            parent2 = parent2.parent
            print(difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio())
        # print("next")
        # print(parent1.name, parent1.attrs, parent1)
        # print(parent2.name, parent2.attrs, parent2)
        return False
        

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
            matches.extend(ArticleProcessing.compare_two_tags(soups[index_a], soups[index_b]))
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

        #articles_sampled = [(e[13], e[1]) for e in data]
        articles_publisher = defaultdict(list)

        for obj in articles_sampled:
            articles_publisher[obj[0]].append(obj[1])


        #new_list = articles_publisher.values()

        res = { publisher: ArticleProcessing.compare_n_tags([BeautifulSoup(e, "html.parser") for e in articles_list], len(articles_list) * 2) for publisher, articles_list in articles_publisher.items()}

        return res