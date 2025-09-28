from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, StorageContext
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor, ImplicitPathExtractor
import os
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from dotenv import load_dotenv

load_dotenv()

# Memgraph Verbindung
username = "neo4j"
password = "deinpasswort"
url = "bolt://localhost:7687"

# Dokumente laden
docs = SimpleDirectoryReader("data/").load_data()

# LLM und Embedding-Modell konfigurieren
LLM = Ollama(os.environ["MODEL"], request_timeout=460)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

Settings.llm = LLM
Settings.chunk_size = 512

# Memgraph Storage Context erstellen
storage_context = Neo4jPropertyGraphStore(
    username=username,
    password=password,
    url=url,
)

# Knowledge Graph Extractors
kg_extractors = [
    #ImplicitPathExtractor(), nur wichtig bei vielen Unterschiedlichen Dokumenten
    DynamicLLMPathExtractor(llm=LLM),
]
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
vector_store = Neo4jVectorStore(
    username=username,
    password=password,
    url="bolt://localhost:7687", 
    embedding_dimension=1024,
    hybrid_search=True  # Kombiniert Vektor- und Keyword-Suche
)



# Index erstellen (ohne explizite Embedding-Konfiguration, da sie automatisch erkannt wird)
index = PropertyGraphIndex.from_documents(
    docs,
    property_graph_store=storage_context,
    embed_model=embed_model,
    kg_extractors=kg_extractors,
    vector_store=vector_store,
    show_progress=True,
    vector_query=True  # aktiviert Vektorsuche
)
