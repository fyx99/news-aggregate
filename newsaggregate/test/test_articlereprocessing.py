import unittest
from newsaggregate.rss.articleprocessing import ArticleProcessing

from newsaggregate.rss.htmlcrawler import HTMLCrawler
from bs4 import BeautifulSoup


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


    test3 =  """<!DOCTYPE html><body><main><article>
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

    testsoup1 = BeautifulSoup(test1, "html.parser").find("article")
    testsoup2 = BeautifulSoup(test2, "html.parser").find("article")
    testsoup3 = BeautifulSoup(test3, "html.parser").find("article")
    testsoup4 = BeautifulSoup(test4, "html.parser").find("article")
        
    def test_compare_two_tags(self):
        # res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup2, 0.8)
        # print(res)
        res = ArticleProcessing.compare_two_tags(self.testsoup3, self.testsoup4, 0.8)
        self.assertEqual(res[0][0], "div")
        print(res)
        # res = ArticleProcessing.compare_two_tags(self.testsoup1, self.testsoup4, 0.8)
        # print(res)
        return
    



    def test_compare_index(self):
        self.assertFalse(ArticleProcessing.compare_index(1))
        a, b = ArticleProcessing.compare_index(2)
        self.assertTrue(a < 2 and b < 2)
        a, b = ArticleProcessing.compare_index(10)
        self.assertTrue(a + b > 0)