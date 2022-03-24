from newsaggregate.rss.manager import RssCrawlManager
from newsaggregate.feed.manager import FeedManager
from newsaggregate.rss.articleprocessing import ArticleProcessingManager
import os


if __name__ == '__main__':

    task = os.environ.get("TASK", default="RSS")
    print(task)
    if task == "RSS":
        RssCrawlManager.main()
    elif task == "FEED":
        FeedManager.main()
    elif task == "REPROCESS_TEXT":
        ArticleProcessingManager.main()
    else:
        print("Not a valid task")
