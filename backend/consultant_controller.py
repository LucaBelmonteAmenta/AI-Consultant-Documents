from config import APP_PATH
from time import sleep
from ast import literal_eval
from typing import List, Optional, Literal, Dict

from langchain_core.documents import Document

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain.agents import Tool, create_react_agent, AgentExecutor


from langchain_core.vectorstores import VectorStoreRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from flashrank import Ranker


from backend.system_prompts import (system_prompt_LLM_keywords, 
                                    system_prompt_query_responder,
                                    description_function_keywords)

from backend.document_loader import DocumentLoaderManager, DocumentSplitter
from backend.embedding_models import EmbeddingModelsManager, HUGGINGFACE_EMBEDDING_MODELS
from backend.vector_database import VectorDatabaseManager
from backend.llm_access import LargeLanguageModelsManager, PAID_SERVICE, LLM_WITHOUT_FUCTION_CALLING
from backend.sigleton_meta import SingletonMeta




class ConsultantController(metaclass=SingletonMeta):

  init: bool = False

  llm_origin: Literal["Gemini Developer API", "OpenAI API", "Ollama"] = None
  name_llm: str = None
  service_token: str = None
  temperature: float = 1.0

  name_embedding_model: str = None
  
  k_index: str = 3
  collection_filter : List[str] = []
  enter_keywords_manually: bool = False
  keywords: str = None

  optimized_database_query_enabled: bool = False
  multi_process_embedding : bool = False

  embedding_manager:EmbeddingModelsManager = None
  database_manager:VectorDatabaseManager = None
  
  
  def __init__(self) -> None:
    self.init = False
    self.embedding_model = None


  def prepare_system(self) -> None:

    self.embedding_model = self.embedding_manager.get_huggingface_embedding_model(model_name=self.name_embedding_model,
                                                                                  multi_process = self.multi_process_embedding)
    self.database_manager = VectorDatabaseManager(self.embedding_model)

    match self.llm_origin:
      case "Gemini Developer API":
        self.llm = LargeLanguageModelsManager.get_google_model(self.service_token, self.name_llm, self.temperature)
      case "OpenAI API":
        self.llm = LargeLanguageModelsManager.get_openai_model(self.service_token, self.name_llm, self.temperature)
      case "Ollama":
        self.llm = LargeLanguageModelsManager.get_ollama_model(self.name_llm, self.temperature)
      case _:
        self.llm = None
        

  @staticmethod
  def register_keywords(keywords:List[str]) -> str:

    list_keywords = literal_eval(keywords) if type(keywords) is str else keywords

    global keywords_for_RAG
    keywords_for_RAG = str(", ".join(list_keywords))

    return keywords_for_RAG
  

  def get_keywords(self, query:str, iterations:int, max_execution_time:int|None) -> str:

    tools = [
      Tool(
          name = "Register Keywords",
          func = ConsultantController.register_keywords,
          description = description_function_keywords,
      )
    ]

    prompt = PromptTemplate.from_template(system_prompt_LLM_keywords)
    agent = create_react_agent(llm=self.llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent,
                                   tools=tools,
                                   verbose=True,
                                   max_iterations=iterations,
                                   handle_parsing_errors="Check your output and make sure it conforms, use the Action/Action Input syntax",
                                   max_execution_time=max_execution_time)
    keywords_for_RAG = ""
    answer = agent_executor.invoke({'input' : query})

    sleep(2)

    if (len(keywords_for_RAG) > 0):
      return keywords_for_RAG
    else:
      return answer['output']

  
  def is_system_configured(self) -> bool:
    llm_conditions_1 = (self.llm_origin in PAID_SERVICE) and (self.service_token is not None) 
    llm_conditions_2 = (self.temperature is not None) and (self.name_llm is not None)
    llm_conditions_3 = self.enter_keywords_manually if self.name_llm in LLM_WITHOUT_FUCTION_CALLING else True
    embedding_conditions = (self.embedding_manager is not None) and (self.name_embedding_model is not None) 
    database_conditions = (self.database_manager is not None) and (len(self.database_manager.get_list_collections()) > 0)
    required_parameters = [self.init, llm_conditions_1, llm_conditions_2, llm_conditions_3, embedding_conditions, database_conditions]
    return all(required_parameters)
  
  
  def answer_query(self, query:str) -> Dict | None:
    if self.is_system_configured():
      
      self.prepare_system()

      if (not ((self.enter_keywords_manually) and (self.keywords is not None))):
        self.keywords = self.get_keywords(query=query, iterations=1, max_execution_time=1000)
        possible_error_messag = "Agent stopped due to iteration limit or time limit."
        if ((self.keywords == possible_error_messag) and (keywords_for_RAG is not None)):
          self.keywords = keywords_for_RAG

      context_docs = self.query_database(query=self.keywords, 
                                         return_retriever=False, 
                                         optimized_database_query=self.optimized_database_query_enabled)
      
      prompt = self.create_prompt(system_prompt_query_responder)
      chain = create_stuff_documents_chain(self.llm, prompt)
      answer = chain.invoke({'input' : query, "context": context_docs})
  
      return {"output": answer ,"context_docs": context_docs, "keywords": self.keywords}
    else:
      return None


  def query_database(self, query: str,
                     return_retriever: Optional[bool] = True,
                     optimized_database_query: Optional[bool] = True,
                     documents_to_filter: Optional[List[str]] = [],
                     ) -> List[Document] | VectorStoreRetriever | ContextualCompressionRetriever:
    
    database = self.database_manager.get_or_create_database()

    if len(documents_to_filter) == 0:
      retriever = database.as_retriever(search_kwargs= { "k": self.k_index } )
    else:
      filter_dict = {"source": {"$in": documents_to_filter}}
      retriever = database.as_retriever(search_kwargs= { "k": self.k_index, 'filter':filter_dict })

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
    model_Multilingual_name = "ms-marco-MultiBERT-L-12"
    model_path = APP_PATH + "/rerank_models/"
    flashrank_client = Ranker(model_name=model_Multilingual_name, cache_dir=model_path)
    compressor = FlashrankRerank(client=flashrank_client, top_n=self.k_index, model=model_Multilingual_name)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,
                                                           base_retriever=retriever)
    return compression_retriever


  def query_with_LLM(self, 
                     llm,
                     query:str,
                     system_prompt_LLM:str,
                     documents_to_filter:List[str]=[]):

    prompt = self.create_prompt(system_prompt_LLM)
    chain = create_stuff_documents_chain(llm, prompt)
    retriever = self.query_database(query=query, 
                                    return_retriever=True, 
                                    optimized_database_query=True, 
                                    documents_to_filter=documents_to_filter)
    rag = create_retrieval_chain(retriever, chain)
    results = rag.invoke({"input": query})

    return results




