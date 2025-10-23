from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.graph_stores.types import EntityNode, ChunkNode, Relation


Settings.embed_model =HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

username = ""
password = ""

url = "bolt://localhost:7687"

graph_store = MemgraphPropertyGraphStore(
    username=username,
    password=password,
    url=url
)

PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,

)

#EntityNode
def event_node(title, rating_average, rating_count, price_value, price_currency, price_unit, duration_min_hours,url,hihlights, full_description,includes, meeting_point)