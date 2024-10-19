import os
from typing import Union, Optional, List

from langchain_core.embeddings.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings



GOOGLE_EMBEDDING_MODELS = ["models/textembedding-gecko@001",
                           "models/textembedding-gecko-multilingual@001",
                           "models/textembedding-gecko@003",
                           "models/text-multilingual-embedding-002",
                           "models/text-embedding-004"] #<-----------#

HUGGINGFACE_EMBEDDING_MODELS = ["BAAI/bge-large-en-v1.5",
                                "BAAI/bge-small-en-v1.5", #<-----------#
                                "sentence-transformers/all-MiniLM-L12-v2", #<-----------#
                                "thenlper/gte-large",
                                "jinaai/jina-embeddings-v2-base-es"]

PATH_EMBEDDING_MODELS = "./embedding_models/"



def get_list_of_installed_embedding_names_models(path_models:str=PATH_EMBEDDING_MODELS) -> List[str]:

  model_names = []

  for item in os.listdir(path_models):
    item_path = os.path.join(path_models, item)
    if ((os.path.isdir(item_path)) and ("models" in item)):
      model_names.append(item.split("models--")[-1])

  return model_names



class EmbeddingModelsManager():

  def __init__(self,
               model_name:str|List[str]=HUGGINGFACE_EMBEDDING_MODELS,
               setup_local_models:bool=True,
               path_models:str=PATH_EMBEDDING_MODELS) -> None:

    self.path_models = path_models
    self.main_model = None

    if (type(model_name) is str):
      self.main_model_name = model_name
      self.list_models_names = [model_name]
      if setup_local_models:
        self.get_huggingface_embedding_model(model_name)
    elif(type(model_name) is list):
      self.list_models_names = model_name
      self.main_model_name = model_name[0]
      if setup_local_models:
        for model_name in self.list_models_names:
            self.get_huggingface_embedding_model(model_name)

  def get_huggingface_embedding_model(self,
                                      model_name:Optional[str] = None,
                                      multi_process: bool = False,
                                      show_progress: bool = True) -> Embeddings:

    model_name = self.main_model_name if model_name is None else model_name

    self.main_model = HuggingFaceEmbeddings(model_name = model_name,
                                            model_kwargs = {"trust_remote_code": True},
                                            cache_folder = self.path_models,
                                            multi_process = multi_process,
                                            show_progress = show_progress)
    return self.main_model


  def embed_query(self, text:str|List[str]) -> List[float] | List[List[float]] | None:

    if self.main_model is None:
      raise ValueError("The embedding model has not been initialized.")

    if type(text) is list:
      return self.main_model.embed_documents(text)
    elif (type(text) is str):
      return self.main_model.embed_query(text)


  def get_google_embedding_model(self, model_name: str) -> Embeddings | None:
    if "GOOGLE_API_KEY" not in os.environ:
      raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
    else:
      self.main_model = GoogleGenerativeAIEmbeddings(model=model_name)
      return self.main_model