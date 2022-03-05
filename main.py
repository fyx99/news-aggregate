from newsaggregate.rss.manager import RssCrawlManager
from newsaggregate.feed.manager import FeedManager
import os


if __name__ == '__main__':

    task = os.environ.get("TASK", default="RSS")
    if task == "RSS":
        RssCrawlManager.main()
    elif task == "FEED":
        FeedManager.main()
    else:
        print("Not a valid task")
