from newsaggregate.rss.manager import RssCrawlManager
from newsaggregate.feed.manager import FeedManager
from newsaggregate.rss.articleprocessing import ArticleProcessingManager
import os
from newsaggregate.logging import get_logger
logger = get_logger()

if __name__ == '__main__':

    task = os.environ.get("TASK", default="RSS")
    logger.info(task)
    logger.debug("Debug level stuff " + task)
    if task == "RSS":
        RssCrawlManager.main()
    elif task == "FEED":
        FeedManager.main()
    elif task == "REPROCESS_TEXT":
        ArticleProcessingManager.main()
    else:
        logger.info("Not a valid task")
