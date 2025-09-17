from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PropertyGraphIndex,SimpleDirectoryReader

from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor



from dotenv import load_dotenv
load_dotenv()
import os

LLM = Ollama(os.environ["MODEL"], request_timeout=460)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
username = ""
password = ""
url = "bolt://localhost:7687"
docs = SimpleDirectoryReader("data/").load_data()

storage = MemgraphPropertyGraphStore(username,password,url)
kg_extractors = [SchemaLLMPathExtractor(llm=LLM)]


from llama_index.core import Settings

# Setze explizit die globalen Einstellungen
Settings.llm = LLM  # Dein Ollama LLM
Settings.embed_model = embed_model  # Dein HuggingFace Embedding Model

graph_rag_retriver = PropertyGraphIndex.from_existing(
    property_graph_store=storage,
    kg_extractors=kg_extractors,
    embed_model=embed_model,
    show_progress=True,
    embed_kg_nodes=True,

)

engine = graph_rag_retriver.as_query_engine(streaming=True)
print(engine.query("Wer ist Charles Robert Darwin"))
