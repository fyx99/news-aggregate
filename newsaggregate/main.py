import os
from logger import get_logger
logger = get_logger()

if __name__ == '__main__':

    task = os.environ.get("TASK", default="RSS")
    logger.info(task)
    logger.debug("DEBUG LOGS VISIBLE RUNNNIG TASK: " + task)

    if task == "RSS":
        from rss.manager import RssCrawlManager
        RssCrawlManager.main()
    elif task == "FEED":
        from feature.manager import FeedManager
        FeedManager.main()
    elif task == "REPROCESS_TEXT":
        from reprocessing.articleprocessing import ArticleProcessingManager
        ArticleProcessingManager.main()
    else:
        logger.info("Not a valid task")
