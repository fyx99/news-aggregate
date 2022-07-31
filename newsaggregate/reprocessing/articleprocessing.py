from bs4 import BeautifulSoup
from bs4.element import Tag
import re, json, time, difflib
from random import randrange, random
from collections import defaultdict, Counter

from db.crud.article import get_article_html, get_articles_for_reprocessing
from db.crud.textpattern import Match, save_unnecessary_text_pattern
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from db.s3 import Datalake

from rss.articleutils import locate_article
from rss.util import Utils

from logger import get_logger
logger = get_logger()


def longer(str1, str2):
    if len(str1) > len(str2):
        return str1
    return str2

class ArticleProcessingManager:

    def save_patterns(db: DatabaseInterface, url_text_patterns):
        for url_pattern, pattern_list in url_text_patterns.items():
            for match in pattern_list:
                match.url_pattern = url_pattern
                save_unnecessary_text_pattern(db, match)

    def main():
        
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)
            articles_html = get_articles_for_reprocessing(di)
            #logger.info("got articles")
            url_text_pattern = ArticleProcessing.reprocess_article_unnecessary_tags(di, articles_html)
            #logger.info("got patterns")
            ArticleProcessingManager.save_patterns(di, url_text_pattern)
            #logger.info("saved pattern")

class ArticleProcessing:

    def get_text_no_script(tag):
        scripts = tag.findAll("script") + tag.findAll("style")
        [s.clear() for s in scripts]
        return tag.get_text()

    def xpath_soup(element):

        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
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
        #logger.info(x,y )
        matches = {k: x[k] for k in x if k in y and x[k] == y[k]}
        if len(matches.keys()) == len(x.keys()):
            return True
        return False
    
    def identifyable(element, test_soup):
        element_count = len(test_soup.findAll(element.name, attrs=element.attrs))
        if element_count > 1:
            return False
        return True

    def identify_useless_parent(tag1, tag2):
        #logger.info("identify usedless")
        parent1 = tag1
        parent2 = tag2
        parent1_text, parent2_text = parent1.get_text(), parent2.get_text()
        result_elements = tag1, tag2
        while parent1 and parent2 and  parent1.parent and parent2.parent and difflib.SequenceMatcher(None, parent1_text, parent2_text).ratio() > 0.8:
            # logger.info(f"Ratio: {difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio()}")
            # logger.info(f"Parent1: {parent1.name}, {parent1.attrs}")
            # logger.info(f"Parent2: {parent2.name}, {parent2.attrs}")

            if parent1.name == parent2.name:
                #logger.info("hit")
                result_elements = parent1, parent2

            parent1, parent2, = parent1.parent, parent2.parent
            parent1_text, parent2_text = parent1.get_text(), parent2.get_text()

            while parent1 and parent2 and parent1.parent and parent2.parent and (parent1.name != parent2.name or not ArticleProcessing.attrs_similar(parent1.attrs, parent2.attrs)):
                if len(parent1_text) > len(parent2_text):
                    parent2 = parent2.parent
                    parent2_text = parent2.get_text()
                    #logger.info("go parent2 up")
                else:
                    #logger.info("go parent1 up")
                    parent1 = parent1.parent
                    parent1_text = parent1.get_text()
            # logger.info(difflib.SequenceMatcher(None, parent1.get_text(), parent2.get_text()).ratio())
            # logger.info(len(parent1.parent.get_text()) , len(parent1.get_text()) , len(parent2.parent.get_text()) , len(parent2.get_text()))
        return result_elements
    
    def get_children(element, only_tags=True):
        return [c for c in element.children if only_tags and type(c) == Tag]
        

    def identifiable_child(element, test_soup):
        identifiable_child = element
        if "Selenskyj rief die Bürger in einer Rede nun dazu auf, weiter Widerstand" in element.get_text():
            a = 1
        while not ArticleProcessing.identifyable(identifiable_child, test_soup) and ArticleProcessing.get_children(identifiable_child):
            biggest_child = None
            for child in ArticleProcessing.get_children(identifiable_child):
                biggest_child = child if not biggest_child or (len(biggest_child.get_text()) < len(child.get_text()) and not child.name in ["script", "style"]) else biggest_child
            if not biggest_child:
                return identifiable_child, ArticleProcessing.identifyable(identifiable_child, test_soup)
            identifiable_child = biggest_child
        # if result element is not identifyable return false -> save as that
        return identifiable_child, (ArticleProcessing.identifyable(identifiable_child, test_soup) or identifiable_child.attrs != {})
        

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
    

    def compare_n_tags(db: DatabaseInterface, articles_list, match_min_occurence=2):
        matches = []
        html_a, html_b = None, None
        
        for index_a in range(len(articles_list) - 1):
            index_b = index_a + 1

            html_a = html_b or get_article_html(db, articles_list[index_a][0])
            html_b = get_article_html(db, articles_list[index_b][0])

            if html_a == None or html_b == None:
                continue
           
            soup_a = BeautifulSoup(locate_article(BeautifulSoup(html_a, "html.parser")).__str__(), "html.parser")
            soup_b = BeautifulSoup(locate_article(BeautifulSoup(html_b, "html.parser")).__str__(), "html.parser")

            start = time.time()
            #logger.info(f"compare {articles_list[index_a][0]} {articles_list[index_a][1]} and {articles_list[index_b][0]} {articles_list[index_b][1]} ")
            res_match = ArticleProcessing.compare_two_tags(soup_a, soup_b, 0.8)
            logger.info(f"{int(time.time()-start)}")
            #logger.info(res_match)
            matches.extend(res_match)

        match_unique_counts = Counter(matches)
        filtered_matches = [match for match, count in match_unique_counts.items() if count >= match_min_occurence]
        return filtered_matches


    def element_saveable(element, identifyable):
        return Match(tag_name=element.name, tag_attrs=json.dumps(element.attrs), tag_xpath=ArticleProcessing.xpath_soup(element), tag_text=re.sub('\s+',' ', element.get_text())[:1000], tag_identifyable=str(identifyable).upper())
        

    def too_similar(txt1, txt2):
        ratio = difflib.SequenceMatcher(None, txt1, txt2).ratio()
        if len(txt1) > 1500 or len(txt2) > 1500:
            return ratio > 0.75
        return ratio > 0.8


    def compare_two_tags(soup1, soup2, min_ratio=0.8, min_len=5, allow_sampling=True):
        p_list1 = [p for p in soup1.findAll("p")]
        p_list2 = [p for p in soup2.findAll("p")]
        matches = []
        # logger.info(difflib.SequenceMatcher(None, "".join([p.get_text() for p in p_list1]), "".join([p.get_text() for p in p_list2])).ratio())
        # logger.info("".join([p.get_text() for p in p_list1]))
        # logger.info("".join([p.get_text() for p in p_list2]))
        full_text1 = "".join([p.get_text() for p in p_list1])
        full_text2 = "".join([p.get_text() for p in p_list2])
        if "€ 19,99 pro Monat" in full_text1 and "€ 19,99 pro Monat" in full_text2:
            #logger.info("pay")
            a = 1
        if ArticleProcessing.too_similar(full_text1, full_text2):
            #logger.info("skip")
            return []

        # if too many entrys just random samples
        max_iterations = 200
        sampling_factor = False
        if len(p_list1) * len(p_list2) > max_iterations:
            sampling_factor = max_iterations / (len(p_list1) * len(p_list2))

        for t1 in p_list1:
            for t2 in p_list2:
                if not allow_sampling or not sampling_factor or random() < sampling_factor:
                    start = time.time()
                    t1_txt, t2_txt = t1.get_text(), t2.get_text()
                    ratio = difflib.SequenceMatcher(None, t1_txt, t2_txt).ratio()
                    if ratio < min_ratio or len(t1_txt) < min_len or len(t1_txt) < min_len:
                        #logger.info(time.time()-start)
                        continue
                    useless_parent1, useless_parent2 = ArticleProcessing.identify_useless_parent(t1, t2)
                    if "data-article-el" in useless_parent1.attrs and (useless_parent1.attrs["data-article-el"][0] in [ "body"] or useless_parent1.attrs["data-article-el"] == "body"):
                        a = 1
                    if useless_parent1 and useless_parent2:
                        useless_parent_id_child1, identifyable1 = ArticleProcessing.identifiable_child(useless_parent1, soup2)
                        #useless_parent_id_child2, identifyable2 = ArticleProcessing.identifiable_child(useless_parent2, soup1)

                        matches.append(ArticleProcessing.element_saveable(useless_parent_id_child1, identifyable1))
                    #logger.info(time.time()-start)
        return matches


    # def clean_attrs_from_individuals(tag, ref_tag):
    #     if tag.name == ref_tag.name:
            

    #     return tag.attrs






    def reprocess_article_unnecessary_tags(db: DatabaseInterface, articles_sampled):
        # returns list of identifications for unnecessary tags

        articles_publisher = defaultdict(list)

        for article in articles_sampled:
            articles_publisher[Utils.get_domain(article[1])].append(article)

        logger.info(f"start with {len(articles_publisher.keys())} groups")
        publisher_patterns = {}
        for publisher, articles_list in articles_publisher.items():
            if len(articles_list) > 20:
                
                start = time.time()
                # old n param , min(len(articles_list) * 2, 1000)
                publisher_patterns[publisher] = ArticleProcessing.compare_n_tags(db, articles_list, 5) 
                logger.info(f"{publisher} {time.time()-start}")


        return publisher_patterns



    
if __name__ == "__main__":
    ArticleProcessingManager.main()

        