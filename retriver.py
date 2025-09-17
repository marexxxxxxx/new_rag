from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PropertyGraphIndex,SimpleDirectoryReader

from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

from dotenv import load_dotenv
load_dotenv()
import os

LLM = Ollama(os.environ["MODEL"], request_timeout=460)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
username = "neo4j"
password = "deinpasswort"
url = "bolt://localhost:7687"
docs = SimpleDirectoryReader("data/").load_data()

storage = Neo4jPropertyGraphStore(username,password,url)
kg_extractors = [SchemaLLMPathExtractor(llm=LLM)]


from llama_index.core import Settings
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
vector_store = Neo4jVectorStore(
    username=username,
    password=password,
    url="bolt://localhost:7687", 
    embedding_dimension=1024,
    hybrid_search=True  # Kombiniert Vektor- und Keyword-Suche
)
# Setze explizit die globalen Einstellungen
Settings.llm = LLM  # Dein Ollama LLM
Settings.embed_model = embed_model  # Dein HuggingFace Embedding Model

graph_rag_retriver = PropertyGraphIndex.from_existing(
    property_graph_store=storage,
    vector_store=vector_store,
    kg_extractors=kg_extractors,
    embed_model=embed_model,
    show_progress=True,
    embed_kg_nodes=True,



)


from llama_index.core.indices.property_graph import TextToCypherRetriever, VectorContextRetriever, TextToCypherRetriever
from llama_index.core.indices.property_graph import (
    PGRetriever,
    VectorContextRetriever,
    LLMSynonymRetriever
)

sub_retrievers = [
    VectorContextRetriever(graph_rag_retriver, ...),
    LLMSynonymRetriever(graph_rag_retriver, ...)
]

retriever = PGRetriever(sub_retrievers=sub_retrievers)

nodes = retriever.retrieve("Wer Ist Charles?")

print(nodes)