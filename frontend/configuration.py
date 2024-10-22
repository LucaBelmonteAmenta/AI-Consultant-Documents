import numpy as np
import pandas as pd
import streamlit as st
from backend.embedding_models import get_list_of_installed_embedding_names_models
from backend.llm_access import LLM_GOOGLE, LLM_OLLAMA, LLM_OPENAI, PAID_SERVICE
from backend.consultant_controller import ConsultantController as Controller



k_explanation_text = """
K: número de fragmentos de documento de la base de datos que es extraído por el LLM por cada consulta, como fuente de información para responder a la misma.\n
Mientas más fragmentos de documentos emplee el modelo, mas tokens consumirá la respectiva consulta realizada. Tome esto en cuenta si emplea un servicio pago para el LLM, o si el mismo posee un límite máximo de tokens por consulta.\n
Tome en cuenta que, a mayor K también aumenta la probabilidad de que uno de los fragmentos extraídos posea la información necesaria para responder a la consulta realizada, pero a la vez aumenta la probabilidad de alucinaciones en la respuesta por parte del LLM.
"""



def ConfigurationUI():

    controller = Controller()
    
    container_embedding = st.container(border=True)
    container_llm = st.container(border=True)
    container_query = st.container(border=True)

    list_embedding_models = get_list_of_installed_embedding_names_models()
    lists_llm = {"Gemini Developer API":LLM_GOOGLE, "Ollama":LLM_OLLAMA, "OpenAI API":LLM_OPENAI}

    
    controller.name_embedding_model = container_embedding.selectbox(label="Seleccione el modelo de embbeding a emplear: ",
                                                                    options=list_embedding_models)


    controller.temperature = container_llm.slider(label="Seleccione la temperatura del LLM: ", 
                                                  max_value=2.0, min_value=0.0, value=1.0, step=0.05)
    controller.llm_origin = container_llm.selectbox(label="Seleccione la fuente del LLM: ",
                                                    options=lists_llm.keys())
    controller.name_llm = container_llm.selectbox(label="Seleccione LLM a emplear: ",
                                                  options=lists_llm[controller.llm_origin])
    controller.service_token = container_llm.text_input(label="Seleccione el token o clave de acceso al LLM (si es que seleccionó un servicio pago como fuente): ",
                                                        disabled=(controller.llm_origin not in PAID_SERVICE))

    
    controller.k_index = container_query.number_input(label="Introduzco el indice K: ", 
                                                      max_value=10, min_value=1, value=3)
    container_query.container(border=True).write(k_explanation_text)




if __name__ == "__main__":
    ConfigurationUI()