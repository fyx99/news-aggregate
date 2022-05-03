import unittest
from db.databaseinstance import DatabaseInterface
from reprocessing.articleprocessing import ArticleProcessing
from logger import get_logger
logger = get_logger()

from bs4 import BeautifulSoup
from rss.util import Utils
from db.s3 import Datalake
from test.test_utils import test_data_func, first_child_n_deep, get_datalake_test_data
from rss.articleutils import locate_article
from db.postgresql import Database
from test import CustomTestcase


class TestArticleProcessing(CustomTestcase):

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
    <p>1234</p>
    <p>Nofsdfssd fdsdrgbfgbzzzzzzzzzzzzzzzjztjtzjsdfsdl Tesdfsdfxt</p>
    <p>Norm fds f cdsnoj fvpods ldsc sdcmsdcsd cspdc sdlcsdcfsd f Text</p>
    <div class="alaa"><span>Das ist recht 1234 unique </span><p>Das ist Werbung und unnötig</p></div>
    </article></main></body>"""

    test5 = """<!DOCTYPE html><body><main><article><p>Veröffentlicht 2022-01-02</p>
    <p>1234</p>
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

        res = ArticleProcessing.compare_two_tags(self.testsoup4, self.testsoup5, 0.8, 3)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].tag_name, "p")
        self.assertEqual(res[0].tag_text, "1234")


    def test_compare_n_tags(self):
        #res = ArticleProcessing.compare_n_tags([self.testsoup1, self.testsoup2, self.testsoup4, self.testsoup3, self.testsoup5], n=100)

        import time
        start = time.time()
        #ArticleProcessingManager.main()
        logger.info(time.time()-start)
        
        return
    

    def test_identifiable_child(self):

        test_text1 = """<article><div><div></div><div><div class="unique"><p>Werbung</p></div></div></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        tag, identifyable = ArticleProcessing.identifiable_child(first_child_n_deep(soup1, 2), soup1)
        self.assertEqual(tag.name, "div")
        self.assertEqual(tag.attrs["class"], ["unique"])
        self.assertTrue(identifyable)
        
            
        test_text2 = """<article><a><a></a><a><a class="unique"><p>Werbung</p></a></a></a></article>"""
        soup2 = BeautifulSoup(test_text2, "html.parser")
        ex = first_child_n_deep(soup2, 3)
        tag, identifyable = ArticleProcessing.identifiable_child(ex, soup2)
        self.assertEqual(tag.name, "a")
        self.assertEqual(tag.attrs, {})
        self.assertFalse(identifyable)



    def test_identifyable(self):
        test_text1 = """<article><div><div><div class="unique"><p>Werbung</p></div></div></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        self.assertFalse(ArticleProcessing.identifyable(first_child_n_deep(soup1, 2), soup1))
        self.assertTrue(ArticleProcessing.identifyable(first_child_n_deep(soup1, 4), soup1))

        test_text1 = """<article><div><div><div class="unique"><p>Werbung</p></div></div><script>3784h0f7ß4fnh3ß48f743f734ßf3498f734ßf34ß897fbn3489f34f7</script></div></article>"""
        soup1 = BeautifulSoup(test_text1, "html.parser")
        self.assertFalse(ArticleProcessing.identifyable(first_child_n_deep(soup1, 2), soup1))
        self.assertTrue(ArticleProcessing.identifyable(first_child_n_deep(soup1, 4), soup1))


    def test_identify_useless_parent(self):
        parent = ArticleProcessing.identify_useless_parent(self.testsoup3.find_all("p")[-1], self.testsoup4.find_all("p")[-1])
        self.assertEqual(parent[0].name, "div")
        self.assertEqual(parent[0].attrs["class"], ["alaa"])
        parent = ArticleProcessing.identify_useless_parent(self.testsoup3.find_all("p")[-1], self.testsoup5.find_all("p")[-1])
        self.assertEqual(parent[0].name, "div")
        self.assertEqual(parent[0].attrs["class"], ["alaa"])
        parent = ArticleProcessing.identify_useless_parent(self.testsoup3.find_all("p")[-2], self.testsoup5.find_all("p")[-1])
        self.assertEqual(parent[0].name, "p")
        parent = ArticleProcessing.identify_useless_parent(self.testsoup3.find("span"), self.testsoup5.find_all("p")[-1])
        self.assertEqual(parent[0].name, "span")
        parent = ArticleProcessing.identify_useless_parent(self.testsoup1.find_all("p")[-1], self.testsoup5.find_all("p")[-1])
        self.assertEqual(parent[0].name, "p")
        parent = ArticleProcessing.identify_useless_parent(self.testsoup1.find_all("p")[-1], self.testsoup5.parent.parent.parent)
        self.assertEqual(parent[0].name, "p")



    def test_compare_two_full_html(self):
        data = [test_data_func(j + ".html") for j in ["sud01","sud02","sud03","sud04", "sud05", "sud06", "tag03", "tag04"]]
        articles_list = [("", "", data[2]), ("", "", data[3])]
        soup_a = BeautifulSoup(locate_article(BeautifulSoup(data[2], "html.parser")).__str__(), "html.parser")
        soup_b = BeautifulSoup(locate_article(BeautifulSoup(data[3], "html.parser")).__str__(), "html.parser")
        case1 = ArticleProcessing.compare_two_tags(soup_a, soup_b, allow_sampling=False)
        self.assertEqual(len(case1), 3)
        tag_texts = [c.tag_text for c in case1]
        self.assertIn('Lesen Sie mehr zum Thema', tag_texts)
        self.assertIn('27. Februar 2022, 14:31 UhrLesezeit: 1 min', tag_texts)
        self.assertIn('FC Chelsea:Was hinter Abramowitschs Manöver stecktDer Klubeigentümer zieht sich beim FC Chelsea zurück - damit gelingt ihm offenbar ein geschickter strategischer Zug. Denn im Hintergrund droht ihm die Beschlagnahmung all seiner Klubanteile.', tag_texts)


        # articles_list = [("", "", data[4]), ("", "", data[5])]
        # case4 = ArticleProcessing.compare_n_tags(articles_list)
        # logger.info(case4)
        # articles_list = [("", "", data[6]), ("", "", data[7])]
        # case4 = ArticleProcessing.compare_n_tags(articles_list)




    def test_compare_index(self):
        self.assertFalse(ArticleProcessing.compare_index(1))
        a, b = ArticleProcessing.compare_index(2)
        self.assertTrue(a < 2 and b < 2)
        a, b = ArticleProcessing.compare_index(10)
        self.assertTrue(a + b > 0)

    
    def test_too_similar(self):
        tx1 = "".join([str(i) for i in range(100)])
        tx2 = "".join([str(i) for i in range(63)]) + "aaaaaa"
        self.assertFalse(ArticleProcessing.too_similar(tx1, tx2))
        tx1 = "".join([str(i) for i in range(100)])
        tx2 = "".join([str(i) for i in range(97)]) + "aaa"
        self.assertTrue(ArticleProcessing.too_similar(tx1, tx2))
        tx1 = "".join(["b" for i in range(2000)])
        tx2 = "".join(["b" for i in range(1000)]) + "".join(["a" for i in range(1000)])
        self.assertFalse(ArticleProcessing.too_similar(tx1, tx2))
        tx1 = "".join([str(i) for i in range(2000)])
        tx2 = "".join([str(i) for i in range(1600)]) + "".join(["a" for i in range(400)])
        self.assertTrue(ArticleProcessing.too_similar(tx1, tx2))
    
    def test_get_domain(self):
        self.assertEqual(Utils.get_domain("https://www.sub.suedzeitung.com/dssdf"), "sub.suedzeitung.com")
        self.assertEqual(Utils.get_domain("https://ex.com/dssdf"), "ex.com")


    def test_get_children(self):

        childs = ArticleProcessing.get_children(self.testsoup1)
        self.assertEqual(len(childs), 5)
        self.assertEqual(childs[0].name, "p")


    def test_full_repro(self):
        html = get_datalake_test_data("4031059")
        soup1  = BeautifulSoup(html, "html.parser")
        soup1 = locate_article(soup1)



        html = get_datalake_test_data("4044506")
        soup2  = BeautifulSoup(html, "html.parser")
        soup2 = locate_article(soup2)

        res = ArticleProcessing.compare_two_tags(soup1, soup2, 0.8, allow_sampling=False)
        # html = get_datalake_test_data("6654762")
        # soup1  = BeautifulSoup(html, "html.parser")     
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)
            #HTMLCrawler.get_patterns(di)
            #HTMLCrawler.run_single(di, Article(url="https://www.westernjournal.com/breaking-academy-announces-will-smiths-punishment-slap-heard-around-world/"))

            #HTMLCrawler.parse_article(soup1, "https://www.westernjournal.com/breaking-academy-announces-will-smiths-punishment-slap-heard-around-world/")

    def test_get_text_no_script(self):
        html = "<div><style>unnötig</style><p>top text</p><p><script>das hier ist script</script></p></div>"
        soup  = BeautifulSoup(html, "html.parser")
        raw_text = soup.get_text()
        clean_text = ArticleProcessing.get_text_no_script(soup)
        self.assertEqual(clean_text, "top text")
        self.assertEqual(raw_text, "top text")




if __name__ == "__main__":

    TestArticleProcessing().test_full_repro()
