from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Settings
import logging
import sys
import nest_asyncio
nest_asyncio.apply()


llm_model = Ollama(model="hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0", request_timeout=460.0)
emebdder = Ollama(model="")
doc = SimpleDirectoryReader("./data/").load_data()

Settings.llm = llm_model

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
    from llama_index.core.indices.property_graph import SchemaLLMPathExtractor, DynamicLLMPathExtractor

    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

    index = PropertyGraphIndex.from_documents(
        doc,
        embed_model=embed_model,
        kg_extractors=[DynamicLLMPathExtractor(
            llm=llm_model
        ),
            SchemaLLMPathExtractor(
                llm=llm_model,
            )
        ],
        property_graph_store=graph_store,
        show_progress=True,
    )


if __name__ == "__main__":
    main()
