import unittest
from newsaggregate.rss.articleprocessing import ArticleProcessing, ArticleProcessingManager

from newsaggregate.rss.htmlcrawler import HTMLCrawler
from bs4 import BeautifulSoup
from newsaggregate.test.test_utils import test_data_func, first_child_n_deep



class TestHTMLCrawler(unittest.TestCase):

    soup1 = BeautifulSoup(HTMLCrawler.get_html('https://www.sueddeutsche.de/politik/ukraine-krieg-russland-waffen-deutschland-1.5537385?reduced=true')[0], "html.parser").find("article")
    soup2 = BeautifulSoup(HTMLCrawler.get_html('https://www.sueddeutsche.de/wirtschaft/schweiz-ukraine-sanktionen-russland-1.5536796')[0], "html.parser").find("article")

    soup1 = BeautifulSoup(HTMLCrawler.get_html('https://www.sueddeutsche.de/sport/ski-alpin-strasser-rast-in-garmisch-auf-rang-drei-1.5537688')[0], "html.parser").find("article")
    soup2 = BeautifulSoup(HTMLCrawler.get_html('https://www.sueddeutsche.de/sport/fussball-russland-ukraine-fifa-reaktion-1.5537542')[0], "html.parser").find("article")

    test1 =  """<!DOCTYPE html><body><main><article>
    <p>Normal Text</p>
    <p>Normasdfsdfsdl sdf sd ffs dsfsdText</p>
    <p>Nofsdfsdrfsdfssdf sdsdf sd sdf f sddfsdfmsdfsdl Tesdfsdfxt</p>
    <p>Normafsdfsf sd sdf dflsd fsd f Text</p>
    <p>Das ist Werbung und unnötig</p>
    </article></main></body>"""

    test2 =  """<!DOCTYPE html><body><main><article>
    <p>Nodcsj cdsdscüdc mdscdscmpdc ds dssfsdTex dfst</p>
    <p>jkl fce ,ndvsl kndvsnmdvsnkldvs ndvsmklödvs nfjh vcfdsjnud nd</p>
    <p>Norm fds fsd  kcsdsndscnkcdsn  klndscndcnkl fsd f Text</p>
    <p>123 Das ist Werbung und unnötig</p>
    </article></main></body>"""


    test3 =  """<!DOCTYPE html><body><main><article><p>Veröffentlicht 2022-01-02</p>
    <p>Normal Text</p>
    <p>scamksackmsakcmlmkscamscmklö</p>
    <p>sa csakopcsa kcsakmopsca kcsapocsa csa</p>
    <p> kcsapomsca ncsacsa kscapmocsa lscajf knvoped lvds</p>
    <div class="alaa"><span>Das ist recht unique </span><p>Das ist Werbung und unnötig</p></div>
    </article></main></body>"""

    test4 =  """<!DOCTYPE html><body><main><article>
    <p>Normasdfs säp  öä. äö   öäöä äö öäöä äö öäö dTex dfst</p>
    <p>Nofsdfssd fdsdrgbfgbzzzzzzzzzzzzzzzjztjtzjsdfsdl Tesdfsdfxt</p>
    <p>Norm fds f cdsnoj fvpods ldsc sdcmsdcsd cspdc sdlcsdcfsd f Text</p>
    <div class="alaa"><span>Das ist recht 1234 unique </span><p>Das ist Werbung und unnötig</p></div>
    </article></main></body>"""

    test5 = """<!DOCTYPE html><body><main><article><p>Veröffentlicht 2022-01-02</p>
    <p>34r34r3f3 4 34 t3t 54 45 45 q  gt uz665 </p>
    <p>unique sdöflmd dsm fds klfkdslfsd fnopsdfds foksd fklsd flk sdfklj sdf</p>
    <p>N i ds jdsoi  ds üiodnd sdü äoin dsd säüdjjkk jö  oä jk dsft</p>
    <div class="alaa"><span>Das ist recht 1234 unique </span><div class="test"><p>Das ist Werbung und unnötig</p></div></div>
    </article></main></body>"""


    testsoup1 = BeautifulSoup(test1, "html.parser").find("article")
    testsoup2 = BeautifulSoup(test2, "html.parser").find("article")
    testsoup3 = BeautifulSoup(test3, "html.parser").find("article")
    testsoup4 = BeautifulSoup(test4, "html.parser").find("article")
    testsoup5 = BeautifulSoup(test5, "html.parser").find("article")
        
    def test_compare_two_tags(self):
        res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup2, 0.8)
        res = ArticleProcessing.compare_two_tags(self.testsoup3, self.testsoup4, 0.8)
        self.assertEqual(res[0].tag_name, "div")
        res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup4, 0.8)
        self.assertEqual(res[0].tag_text, "Das ist Werbung und unnötig")
        res = ArticleProcessing.compare_two_tags(self.testsoup4, self.testsoup5, 0.8)
        self.assertEqual(res[0].tag_attrs, """{"class": ["alaa"]}""")
        res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup5, 0.8)
        self.assertEqual(res[0].tag_name, "p")
        res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup1, 0.8)
        self.assertEqual(res, [])

        return

    def test_compare_n_tags(self):
        #res = ArticleProcessing.compare_n_tags([self.testsoup1, self.testsoup2, self.testsoup4, self.testsoup3, self.testsoup5], n=100)

        import time
        start = time.time()
        #ArticleProcessingManager.main()
        print(time.time()-start)
        
        return
    

    def test_identifiable_child(self):

        test_text1 = """<article><div><div></div><div><div class="unique"><p>Werbung</p></div></div></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        res = ArticleProcessing.identifiable_child(first_child_n_deep(soup1, 2), soup1)
        self.assertEqual(res.name, "div")
        self.assertEqual(res.attrs["class"], ["unique"])
        
            
        test_text2 = """<article><a><a></a><a><a class="unique"><p>Werbung</p></a></a></a></article>"""
        soup2 = BeautifulSoup(test_text2, "html.parser")
        res = ArticleProcessing.identifiable_child(first_child_n_deep(soup1, 2), soup2)
        self.assertEqual(res.attrs, {})



    def test_identifyable(self):
        test_text1 = """<article><div><div><div class="unique"><p>Werbung</p></div></div></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        self.assertFalse(ArticleProcessing.identifyable(first_child_n_deep(soup1, 2), soup1))
        self.assertTrue(ArticleProcessing.identifyable(first_child_n_deep(soup1, 4), soup1))

        test_text1 = """<article><div><div><div class="unique"><p>Werbung</p></div></div><script>3784h0f7ß4fnh3ß48f743f734ßf3498f734ßf34ß897fbn3489f34f7</script></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        self.assertFalse(ArticleProcessing.identifyable(first_child_n_deep(soup1, 2), soup1))
        self.assertTrue(ArticleProcessing.identifyable(first_child_n_deep(soup1, 4), soup1))





    def test_compare_n(self):
        data = [test_data_func(j) for j in ["sud01","sud02","sud03","sud04", "sud05", "sud06"]]
        articles_list = [("", "", data[2]), ("", "", data[3])]
        case1 = ArticleProcessing.compare_n_tags(articles_list, n=1, match_min_occurence=0)
        self.assertEqual(len(case1), 3)
        tag_texts = [c.tag_text for c in case1]
        self.assertIn('Lesen Sie mehr zum Thema', tag_texts)
        self.assertIn('27. Februar 2022, 14:31 UhrLesezeit: 1 min', tag_texts)
        self.assertIn('FC Chelsea:Was hinter Abramowitschs Manöver stecktDer Klubeigentümer zieht sich beim FC Chelsea zurück - damit gelingt ihm offenbar ein geschickter strategischer Zug. Denn im Hintergrund droht ihm die Beschlagnahmung all seiner Klubanteile.', tag_texts)


        # case2 = ArticleProcessing.compare_n_tags([BeautifulSoup(d, "html.parser").find("article") for d in [data[0], data[1]]], n=1)

        # print(case2)

        #case3 = ArticleProcessing.compare_n_tags([BeautifulSoup(d, "html.parser").find("article") for d in [data[0], data[3]]], n=1)
        articles_list = [("", "", data[4]), ("", "", data[5])]
        case4 = ArticleProcessing.compare_n_tags(articles_list, n=1)
        print(case4)

    def test_compare_index(self):
        self.assertFalse(ArticleProcessing.compare_index(1))
        a, b = ArticleProcessing.compare_index(2)
        self.assertTrue(a < 2 and b < 2)
        a, b = ArticleProcessing.compare_index(10)
        self.assertTrue(a + b > 0)

    

if __name__ == "__main__":
    ArticleProcessingManager.main()

        