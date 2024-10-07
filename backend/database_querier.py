from typing import List

from langchain_core.documents import Document

from langchain_chroma import Chroma as Chroma_langchain

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.vectorstores import VectorStoreRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank

from backend.document_loader import DocumentLoaderManager
from backend.embedding_models import EmbeddingModelsManager
from backend.vector_database import VectorDatabaseManager
from backend.llm_access import LargeLanguageModelsManager



class DatabaseQuerier():

  def __init__(self,
               chroma_local:Chroma_langchain,
               number_of_results:int=8) -> None:

    self.chroma_local = chroma_local
    self.number_of_results = number_of_results


  def query_database(self, query:str,
                     return_retriever:bool=True,
                     optimized_database_query:bool=True,
                     documents_to_filter:List[str]=[],
                     ) -> List[Document] | VectorStoreRetriever | ContextualCompressionRetriever:

    if len(documents_to_filter) == 0:
      retriever = self.chroma_local.as_retriever(search_kwargs= { "k": self.number_of_results } )
    else:
      filter_dict = {"source": {"$in": documents_to_filter}}
      retriever = self.chroma_local.as_retriever(search_kwargs= { "k": self.number_of_results, 'filter':filter_dict })

    if optimized_database_query:
       retriever = self.get_compression_retriever(retriever)

    if return_retriever:
      return retriever
    else:
      return retriever.invoke(query)


  def create_prompt(self, system_prompt:str) -> ChatPromptTemplate:

    system_prompt_context = (system_prompt + "\n\n" + "{context}")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_context),
            ("human", "{input}"),
        ])

    return prompt


  def get_compression_retriever(self, retriever:VectorStoreRetriever) -> ContextualCompressionRetriever:
    compressor = FlashrankRerank(top_n=self.number_of_results)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,
                                                           base_retriever=retriever)
    return compression_retriever


  def query_with_LLM(self, llm,
                     query:str,
                     system_prompt_LLM:str,
                     documents_to_filter:List[str]=[],):

    prompt = self.create_prompt(system_prompt_LLM)
    chain = create_stuff_documents_chain(llm, prompt)
    retriever = self.query_database(query, True, True, documents_to_filter)
    rag = create_retrieval_chain(retriever, chain)
    results = rag.invoke({"input": query})

    return results


