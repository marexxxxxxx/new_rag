from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.graph_stores.types import EntityNode, ChunkNode, Relation
from state import state
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="hf.co/leliuga/all-MiniLM-L6-v2-GGUF:F16")

Settings.embed_model =HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
Settings.llm=None

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
def event_node(name, rating_average,rating_count,price_value,price_currency,price_unit,duration_min_hours,url,highlights,full_description,includes,meeting_point):
    event_node = EntityNode(
        name=name,
        label="event",
        properties={
            "name":name,
            "rating_average": rating_average,
            "rating_count":rating_count,
            "price_value":price_value,
            "price_currency":price_currency,
            "price_unit":price_unit,
            "duration_min_hours":duration_min_hours,
            "url":url,
            #advanced
            "highlights":highlights,
            "full_description":full_description,
            "includes":includes,
            "meeting_point":meeting_point
        }
    )

    embeddings_description = embedder.embed_query(str(full_description['full_description']))
    embedding = ChunkNode(
        text=str(full_description['full_description']),
        embedding=embeddings_description,
        meta_data={}
    )

    all = [embeddings_description,embedder]
    relation = Relation(
        label="HAS_DESCRIPTION",
        source_id=event_node.id,
        target_id=embedding.id,
        properties={"relationship_type": "content"}
    )
    graph_store.upsert_nodes([embedding,event_node])
    graph_store.upsert_relations([relation])
import attr
def builder(state:state):
    get_current_node, new_ergebnisse = state["result_list"][0], state["result_list"]
    new_ergebnisse.pop(0)
    basic, advanced = get_current_node.ActivityListing, get_current_node.Advanced

    event_node(**basic.dict(), **advanced.dict())
    return {"result_list":new_ergebnisse}