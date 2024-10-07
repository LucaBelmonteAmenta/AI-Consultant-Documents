from typing import Optional, List
from langchain_core.documents import Document

from re import split as re_split
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.document_loaders.xml import UnstructuredXMLLoader
from langchain.document_loaders.html import UnstructuredHTMLLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 300

SEPARATORS_DEFAULTS = ["\n\n\n",
                       "\n\n",
                       "\n",
                       " ",
                       ".",
                       ",",
                       "\u200b",  # Zero-width space
                       "\uff0c",  # Fullwidth comma
                       "\u3001",  # Ideographic comma
                       "\uff0e",  # Fullwidth full stop
                       "\u3002",  # Ideographic full stop
                       ""]

FILES_DIRECTORY = "./data"

LOADERS = {'.csv': CSVLoader,
           '.txt': TextLoader,
           '.pdf': PyMuPDFLoader,
           '.xml': UnstructuredXMLLoader,
           '.doc': UnstructuredWordDocumentLoader,
           '.docx': UnstructuredWordDocumentLoader,
           '.pptx': UnstructuredPowerPointLoader,
           '.pptm': UnstructuredPowerPointLoader,
           '.ppt': UnstructuredPowerPointLoader,
           '.md': UnstructuredMarkdownLoader,
           '.html': UnstructuredHTMLLoader,
           '.htm': UnstructuredHTMLLoader}



class DocumentLoaderManager():

  @staticmethod
  def create_directory_loader(directory_path: str, file_type : str = '.pdf') -> DirectoryLoader:

    loader = DirectoryLoader(path=directory_path,
                            glob=f"**/*{file_type}",
                            silent_errors=True,
                            loader_cls=LOADERS[file_type])
    return loader

  @staticmethod
  def create_file_loader(file_path: str, file_type: str):

    if file_type in LOADERS.keys():
      loader = LOADERS[file_type](file_path=file_path)
    else:
      loader = UnstructuredFileLoader(file_path=file_path)

    return loader

  @classmethod
  def get_document(cls, file_path : str, docs: List[Document] = []) -> List[Document]:

    file_type = "." + file_path.split(".")[-1]

    loader = cls.create_file_loader(file_path, file_type)
    docs += loader.load()

    return docs

  @classmethod
  def get_documents_from_directory(cls, directory_path : str = FILES_DIRECTORY,
                                   file_type : Optional[str] = None,
                                   docs: List[Document] = [] ):

    if file_type is None:
      for type_document, type_loader in LOADERS.items():
        loader = cls.create_directory_loader(directory_path, type_document)
        docs += loader.load()
    else:
      loader = cls.create_directory_loader(directory_path, file_type)
      docs += loader.load()

    return docs



class DocumentSplitter():

  def __init__(self, separators:List[str] = SEPARATORS_DEFAULTS) -> None:
    self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                                        chunk_overlap=CHUNK_OVERLAP,
                                                        separators=separators,
                                                        strip_whitespace=True,
                                                        add_start_index=True,
                                                        length_function=len,
                                                        is_separator_regex=False)


  def split_documents(self, docs : List[Document], source_name: str|None = None) -> List[Document]:

    splits = self.text_splitter.split_documents(docs)

    for idx, text in enumerate(splits):
      if source_name is not None:
        splits[idx].metadata['source'] = source_name
      else:
        splits[idx].metadata['source'] = re_split(r"\.|/", splits[idx].metadata['source'])[-2]

    return splits