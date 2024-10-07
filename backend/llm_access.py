from enum import Enum
from typing import Literal

from langchain_openai import OpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI



LLM_GOOGLE = ["gemini-1.5-pro-exp-0801",
              "gemini-1.5-flash",
              "gemini-1.5-pro",
              "gemini-1.5-pro-002",
              "gemini-1.5-flash-8b"]

LLM_OPENAI = ["gpt-3.5-turbo-instruct",
              "gpt-3.5-turbo",
              "text-davinci-003",
              "gpt-4o-mini",
              "gpt-4o"]

LLM_OLLAMA = ["llama3.2",
              "gemma2",
              "mistral-nemo"]



class LargeLanguageModelsManager():

    @staticmethod
    def get_google_model(self, 
                         api_key:str, 
                         name_model:str=LLM_GOOGLE[0], 
                         temperature:int=0.0) -> ChatGoogleGenerativeAI:
        
        return ChatGoogleGenerativeAI(model=name_model,
                                      temperature=temperature,
                                      max_tokens=None,
                                      timeout=None,
                                      max_retries=3,
                                      api_key=api_key)
    

    @staticmethod
    def get_openai_model(self, 
                         api_key:str, 
                         name_model:str=LLM_OPENAI[0], 
                         temperature:int=0.0) -> OpenAI:
        
        return  OpenAI(model=name_model,
                       temperature=temperature,
                       max_tokens=None,
                       timeout=None,
                       max_retries=3,
                       api_key=api_key)
    

    @staticmethod
    def get_ollama_model(self, 
                         name_model:str=LLM_OLLAMA[0], 
                         temperature:int=0) -> OllamaLLM:
        
        return  OllamaLLM(model=name_model,
                          temperature=temperature,
                          max_tokens=None,
                          timeout=None,
                          max_retries=3)





    

    