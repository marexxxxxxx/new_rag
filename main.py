from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader

import logging
import sys



llm_model = Ollama(model="gpt-oss:20b", request_timeout=460.0)
emebdder = Ollama(model="")
doc = SimpleDirectoryReader("./data/").load_data()

def main():
    username = ""  # Your Memgraph username, default is ""
    password = ""  # Your Memgraph password, default is ""
    url = "bolt://localhost:7687"  # Connection URL for Memgraph

    graph_store = MemgraphPropertyGraphStore(
        username=username,
        password=password,
        url=url,
    )
    
    from llama_index.core import PropertyGraphIndex
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

    # Embedding-Modell: BAAI/bge-m3
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

    # LLM: gpt-oss20b

    index = PropertyGraphIndex.from_documents(
        doc,
        embed_model=embed_model,
        kg_extractors=[
            SchemaLLMPathExtractor(
                llm=llm_model,
            )
        ],
        property_graph_store=graph_store,
        show_progress=True,
    )
    query_engine = index.as_query_engine(include_text=True)

    response = query_engine.query("Who did Charles Robert Darwin collaborate with?")
    print(str(response))




if __name__ == "__main__":
    main()
