from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, StorageContext
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor, ImplicitPathExtractor
import os
from dotenv import load_dotenv

load_dotenv()

# Memgraph Verbindung
username = ""
password = ""
url = "bolt://localhost:7687"

# Dokumente laden
docs = SimpleDirectoryReader("data/").load_data()

# LLM und Embedding-Modell konfigurieren
LLM = Ollama(os.environ["MODEL"], request_timeout=460)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

Settings.llm = LLM
Settings.chunk_size = 512

# Memgraph Storage Context erstellen
storage_context = MemgraphPropertyGraphStore(
    username=username,
    password=password,
    url=url,
)

# Knowledge Graph Extractors
kg_extractors = [
    ImplicitPathExtractor(),
    DynamicLLMPathExtractor(llm=LLM),
]

# Index erstellen (ohne explizite Embedding-Konfiguration, da sie automatisch erkannt wird)
index = PropertyGraphIndex.from_documents(
    docs,
    property_graph_store=storage_context,
    embed_model=embed_model,
    kg_extractors=kg_extractors,
    show_progress=True,
)
