import datetime
import langchain
import os
import weaviate
from langchain.vectorstores import Weaviate

from .chain import get_new_chain1

WEAVIATE_URL = os.environ["WEAVIATE_URL"]


def get_weaviate_store():
    client = weaviate.Client(url=WEAVIATE_URL,)
    return Weaviate(client, "Paragraph", "content", attributes=["source"])

vectorstore = get_weaviate_store()
qa_chain = get_new_chain1(vectorstore)

def chat(inp, history):    
    print("\n==== date/time: " + str(datetime.datetime.now()) + " ====")
    print("inp: " + inp)
    history = history or []
    output = qa_chain({"question": inp, "chat_history": history})
    answer = output["answer"]
    history.append((inp, answer))
    print(history)
    return history