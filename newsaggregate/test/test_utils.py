from bs4.element import Tag
from db.s3 import Datalake

from logger import get_logger
logger = get_logger()


def test_data_func(tests):
    with open(f"test/testdata/{tests}", mode="r", encoding="utf-8") as file:
        return file.read()


def mock_data(prefix, filetype=None):
    if filetype == "html":
        with open(f"test/testdata/{prefix}.html") as htmlfile:
            return htmlfile.read()
    try:
        with open(f"test/testdata/{prefix}.txt") as txtfile, open(f"test/testdata/{prefix}.html") as htmlfile:
            return txtfile.read(), htmlfile.read()
    except FileNotFoundError:
        logger.error("File not found")
        return "", ""

def get_children(element, only_tags=True):
    return [c for c in element.children if only_tags and type(c) == Tag]
    
def first_child_n_deep(element, n):
    child = element
    for _ in range(n):
        child = get_children(child)[0]
    return child



def get_datalake_test_data(id):
    with Datalake() as dl:
        res = dl.get_json(f"testing/article_html/{id}")["html"]
        return res
    