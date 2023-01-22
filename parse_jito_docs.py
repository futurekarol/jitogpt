from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import requests
import urllib.parse
from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate
import os

docs = []
metadatas = []


def scrape_gitbook(base_url):
    sitemap = requests.get(base_url + "/sitemap.xml").content
    sitemap_soup = BeautifulSoup(sitemap, "xml")

    urls = sitemap_soup.find_all("url")
    url_list = []
    for url in urls:
        loc = url.find("loc").text
        url_list.append(loc)

    for url in url_list:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        main = soup.find("main")
        for href in main.find_all("a"):
            href["href"] = urllib.parse.urljoin(base_url, href.get("href"))
        for img in main.find_all("img"):
            img.decompose()

        print(url)
        main.findChildren(recursive=False)[-1].findChildren(recursive=False)[-1].decompose()

        docs.append(md(str(main)))
        metadatas.append({"source": url})


text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "#", " ", ""],
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len,
)

scrape_gitbook("https://jito-labs.gitbook.io/mev")
scrape_gitbook("https://jito-foundation.gitbook.io/jitosol")
scrape_gitbook("https://jito-foundation.gitbook.io/mev")

documents = text_splitter.create_documents(docs, metadatas=metadatas)

print(documents)

WEAVIATE_URL = os.environ["WEAVIATE_URL"]
client = weaviate.Client(
    url=WEAVIATE_URL,
)

# client.schema.delete_class("Paragraph")
# client.schema.get()
schema = {
    "classes": [
        {
            "class": "Paragraph",
            "description": "A written paragraph",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text",
                }
            },
            "properties": [
                {
                    "dataType": ["text"],
                    "description": "The content of the paragraph",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False,
                        }
                    },
                    "name": "content",
                },
                {
                    "dataType": ["text"],
                    "description": "The link",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True,
                            "vectorizePropertyName": False,
                        }
                    },
                    "name": "source",
                },
            ],
        },
    ]
}

client.schema.create(schema)



with client.batch as batch:
    for text in documents:
        batch.add_data_object(
            {"content": text.page_content, "source": str(text.metadata["source"])},
            "Paragraph",
        )

