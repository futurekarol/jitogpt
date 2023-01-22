import os
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate


docs = []
metadatas = []

dirs = [
   # ("git_sources/jito-programs/", "https://github.com/jito-foundation/jito-programs/blob/master/"),
   # ("git_sources/geyser-grpc-plugin/", "https://github.com/jito-foundation/geyser-grpc-plugin/blob/master/"),
   # ("git_sources/jito-solana/core/", "https://github.com/jito-foundation/jito-solana/blob/master/core/"),
   ("git_sources/searcher-examples/", "https://github.com/jito-labs/searcher-examples/blob/master/")
]

for (dir, base_url) in dirs:
    for p in Path(dir).rglob("*"):
        if p.is_dir():
            continue
        with open(p) as f:
            docs.append(f.read())
            source = str(p).replace(dir, base_url)
            metadatas.append({"source": p})


text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "#", "}", " ", ""],
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len,
)

documents = text_splitter.create_documents(docs, metadatas=metadatas)

WEAVIATE_URL = os.environ["WEAVIATE_URL"]
client = weaviate.Client(
    url=WEAVIATE_URL,
)

with client.batch as batch:
    for text in documents:
        batch.add_data_object(
            {"content": text.page_content, "source": str(text.metadata["source"])},
            "Paragraph",
        )

