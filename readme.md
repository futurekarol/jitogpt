# jitoGPT

JitoGPT is a chatbot designed to assist validators, stakers, and searchers with all things Jito. Utilizing the power of GPT-3, this chatbot can provide accurate and reliable information on Jito's mechanics, as well as answer questions related to the topic. Built for the LamportDAO hackathon.

This repository contains the LLM logic as well as the scraping code used. Does not inlude the frontend yet bcs the folder is too much of a mess to upload rn without exposing half of my API keys. The frontend is very basic anyway.

## Design 
The design is based on this blog post: https://blog.langchain.dev/langchain-chat/

Essentially first ingest data:
1. Scrape the data sources (here jito docs and github).
2. Split them into 2000 letter chunks (~500 openai tokens).
3. Create embeddings through OpenAI for those chunks. Embeddings are vectors. If you measure the vector distance between two embeddings you get how close they are semantically. I.e. `Einstein` and `Theory of Relativity` would be close to each other.
4. Store those embeddings in a vector database. I use weaviate here.

Then when a user starts a new chat session:
1. Create an embedding for the question
2. Query the vector db for the n closest data chunks to the question. this gives us the semantically most relevant pieces of docs/ code
3. Create a prompt containing the most relevant docs (from 2.), the question, and some stuff that instructs gpt3 how to respond.
4. Send to OpenAI API and return response to user

Finally for sessions with chat history. The problem is that chat history can quickly become more than the max prompt size. When the user asks a follow up question.
1. Let gpt3 create a new question from the chat history and the follow up question. We use the technique of few-shot prompting here.
2. Create an embedding for the new question. Then the rest is same when a user starts a new session.


### Stack
- **Frontend**: Simple html with https://htmx.org/. wanted to try a new (old) way to build frontends that isn't complicated like react. so far pretty cool
- **Web Backend**: Django with gunicorn as webserver for dynamic content. Deployed on Kubernetes on GCP. It is a bit of a clusterfuck bcs I have no idea what I am doing, thats why this isn't in the repo yet.
All of this sits behind Cloudflare
- **Vectorstore**: Weaviate deployed on K8s https://weaviate.io/developers/weaviate/installation/kubernetes
 set up was super smooth. and it has plugins to automatically create embeddings through openai. Only once I broke the database beyond repair lol
- **LLM Chain**: Using Langchain https://github.com/hwchase17/langchain because of the blogpost and because people have been raving about it. Pretty cool I guess. But ultimately in production you will need extend all the classes to have room for proper logging, analytics and caching.


### Files
- `chain.py`: The LLM chain build with Langchain
- `chat.py`: How I interact with the chain in Django
- `ingest_examples.py`: Script to ingest examples for few-shot prompts for rephrasing the question with history
- `parse_jito_docs.py`: Script to get the text from the jito gitbooks and dump them into weaviate
- `parse_repositories.py`: Script to eat through the jito github repositories. beware of doing the solana core in one go. this failed for me multiple times and broke weaviate. but idk when i tried ingesting the data i also had bad internet