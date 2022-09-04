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
from test.custom_testcase import CustomTestcase


class TestArticleProcessing2(CustomTestcase):

    def test1(self):
        return


    u1 = "https://www.dailymail.co.uk/femail/article-10915009/Amazon-reduced-ECOWISH-summer-dress-39-99-making-dressing-warm-weather-easier.html"

    t1out = [
        "By Zoe Griffin For Dailymail.com",
        "Published: 13:08 BST, 17 June 2022 | Updated: 15:42 BST, 17 June 2022",
        "Products featured in this article are independently selected by our shopping writers. If you make a purchase using links on this page, DailyMail.com will earn an affiliate commission."
    ]

    text1 = "By Zoe Griffin For Dailymail.com Published: 13:08 BST, 17 June 2022 | Updated: 15:42 BST, 17 June 2022  50 View comments  Products featured in this Mail Best article are independently selected by our shopping writers. If you make a purchase using links on this page, DailyMail.com may earn an affiliate commission. Normally a dress that receives lots of compliments comes at a great expense, but thousands of Amazon shoppers are saying the ECOWISH spaghetti strap swing skater dress gets positive attention with each wear and it’s just $39.99 in some colors. With a strapless back and a floaty skater skirt and made from lightweight, breathable material, this has all the detail usually reserved for designer outfits for a fraction of the price. A white dress is a summer essential and the ECOWISH dress will take you from day to night in style. It securely supports your bust, slims the waist and feels light and breezy thanks to the full skirt. A lace trim and embellishment on the bust plus a ruffled hem make it look more expensive than it is. White makes any tan pop but there are 26 color and print options. A white dress is a closet essential in summer and the ECOWISH strappy skater dress is affordable, flattering and comfortable according to thousands of Amazon shoppers As you can dress it down with white sneakers or flip flops and wear with wedges or high sandals for a night out, this versatile dress will be an item that you’ll get a lot of use out over the coming months. Switch up your accessories and you can make it look different each time. And even better news is that it’s extremely figure flattering thanks to the wide waistband and full skirt. This ensures your tummy is pulled in and the effect of the full skirt also means your waist looks smaller in comparison to your hips. With more than 15,000 five star reviews on Amazon, shoppers say the only problem they have is working out what color to buy it in, but some eliminate that issue by snapping it up in several. Emerald green and pastel pink are two of the 26 color options available for the ECOWISH swing skater dress Designer fashion from $32.99 - Amazon shoppers are stunned by the quality of the ECOWISH dress given it's affordable price 'I got soooo many compliments with this dress,' wrote one shopper. 'Fits perfectly, great stitching and best of all it's not see-through. I will definitely get a lot of wear out of it this summer.' Another added: 'I'm in love. This is the cutest little summer dress ever. I now have it in three colors.' The ECOWISH strappy dress is available with either a wide lace waistband or a wide bow tie waistband, which shoppers say is more stretchy. The bow can be adjusted perfectly to fit your shape, and readjusted if you're going out to dinner or want to loosen it slightly. Prefer florals to block colors? The ECOWISH strappy skater dress is available in several prints that grab attention and feel fresh while the fit of the dress makes you feel extra confident Prefer something with sleeves? ECOWISH also has a couple of equally great value dresses with slightly more coverage. Soft, comfortable, breathable, lightweight and comfortable to touch and wear, this dress checks all the boxes. Casual and flowy, it will keep you feeling cool whatever the weather. The bobble detail makes it look a lot more expensive than $33. This A-line dress can be styled up or down for multiple occasions this summer. Equally great for a wedding or a beach day, its ultra versatile. Available in summer floral print or leopard print, you can go for cute and girly or choose something with a little more bite.  Share what you think The comments below have not been moderated. The views expressed in the contents above are those of our users and do not necessarily reflect the views of MailOnline. By posting your comment you agree to our house rules. Do you want to automatically post your MailOnline comments to your Facebook Timeline? Your comment will be posted to MailOnline as usual.  Do you want to automatically post your MailOnline comments to your Facebook Timeline? Your comment will be posted to MailOnline as usual We will automatically post your comment and a link to the news story to your Facebook timeline at the same time it is posted on MailOnline. To do this we will link your MailOnline account with your Facebook account. We’ll ask you to confirm this for your first post to Facebook. You can choose on each post whether you would like it to be posted to Facebook. Your details from Facebook will be used to provide you with tailored content, marketing and ads in line with our Privacy Policy. Published by Associated Newspapers Ltd Part of the Daily Mail, The Mail on Sunday & Metro Media Group"


if __name__ == "__main__":

    TestArticleProcessing2()
