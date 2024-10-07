from typing import Sequence, Optional, List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_core.documents import Document

import chromadb as Chroma_core
from chromadb.api.models.Collection import Collection
from langchain_chroma import Chroma as Chroma_langchain

from chromadb.utils.embedding_functions.chroma_langchain_embedding_function import create_langchain_embedding


PATH_DATABASE = "./database"


class VectorDatabaseManager():

  def __init__(self,
               embeddings_model_langchain:HuggingFaceEmbeddings|GoogleGenerativeAIEmbeddings,
               path_database:str=PATH_DATABASE) -> None:

    if (type(embeddings_model_langchain) is HuggingFaceEmbeddings):
      model_name = embeddings_model_langchain.model_name
    elif (type(embeddings_model_langchain) is GoogleGenerativeAIEmbeddings):
      model_name = embeddings_model_langchain.model
    else:
      model_name = None

    if (type(model_name) is str):
      self.path_database = f"{path_database}/{model_name}"
    else:
      self.path_database = path_database

    self.embeddings_model = embeddings_model_langchain

    self.get_or_create_database(path_database)


  def get_or_create_database(self,
                             path_database:Optional[str]= None,
                             collection_name:str = "main_collection") -> Chroma_langchain:

    if path_database is None:
      path_database = self.path_database

    return Chroma_langchain(collection_name=collection_name,
                            persist_directory=path_database,
                            embedding_function=self.embeddings_model)


  def get_or_create_collection(self, collection_name:str) -> Collection:

    embeddings_function = create_langchain_embedding(self.embeddings_model)
    client = Chroma_core.PersistentClient(path=self.path_database)
    collection = client.get_or_create_collection(name=collection_name,
                                                 embedding_function=embeddings_function)

    return collection


  def delete_collection(self, collection_name:str):
    embeddings_function = create_langchain_embedding(self.embeddings_model)
    client = Chroma_core.PersistentClient(path=self.path_database)
    collection = client.delete_collection(name=collection_name)


  def get_list_collections(self)-> Sequence[Collection]:
    return Chroma_core.PersistentClient(path=self.path_database).list_collections()


  def modify_collection_name(self, old_name:str, new_name:str):
    collection = self.get_or_create_collection(old_name)
    collection.modify(new_name)


  def add_documents(self,
                    documents:List[Document],
                    collection_name:str = "main_collection") -> List[str]:

    Chroma_langchain_local = self.get_or_create_database(self.path_database,
                                                         collection_name)

    return Chroma_langchain_local.add_documents(documents)


  def get_documents_list(self, name_collection:Optional[str|List[str]]=None) -> List[str]:

    client = Chroma_core.PersistentClient(path=self.path_database)

    z = ["embeddings", "documents", "metadatas"]

    if (name_collection is None):
      collections_list = [collection.name for collection in self.get_list_collections()]
    elif (type(name_collection) is str):
      collections_list = [name_collection]
    elif (type(name_collection) is list):
      collections_list = name_collection
    else:
      raise ValueError("name_collection must be a string or a list of strings")

    documents_list = []

    for collection_name in collections_list:

      # Obtén los datos de la colección
      collection_data = client.get_collection(collection_name).get()

      # Extrae los metadatos
      metadatas = collection_data['metadatas']

      # Obtén los valores únicos de 'source'
      if metadatas is not None:

        sources = set()
        for metadata in metadatas:
            source = metadata.get('source', None)
            if source:
                sources.add(source)

        # Obtener solo el nombre de archivo de cada ruta
        documents_list.extend(list(set(source.split('/')[-1] for source in sources)))

    return documents_list




