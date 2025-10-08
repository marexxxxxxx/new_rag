from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
vector_store = Neo4jPropertyGraphStore(
    username=username,
    password=password,
    url="bolt://localhost:7687", 
)

from llama_index.core import  StorageContext, load_index_from_storage
index = PropertyGraphIndex.from_existing(
    graph_stores=vector_store,
    embed_kg_nodes=True
)


from llama_index.core.indices.property_graph import VectorContextRetriever, PGRetriever

sub_retriver = [VectorContextRetriever(
    index.property_graph_store,
    embed_model=embed_model,
    include_text=False,
    similarity_top_k=2,
    path_depth=1
)]
retriever = PGRetriever(sub_retrievers=sub_retriver)
nodes = retriever.retrieve("Wie stehen Amazon und Meta zueinader")
