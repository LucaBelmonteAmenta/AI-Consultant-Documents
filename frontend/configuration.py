import streamlit as st
from backend.embedding_models import get_list_of_installed_embedding_names_models
from backend.llm_access import LLM_GOOGLE, LLM_OLLAMA, LLM_OPENAI, PAID_SERVICE
from backend.consultant_controller import ConsultantController as Controller



def ConfigurationUI():

    controller = Controller()
    
    container_embedding = st.container(border=True)
    container_llm = st.container(border=True)
    container_database = st.container(border=True)

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
    controller.service_token = container_llm.text_input(label="Ingrese el token o clave de acceso al LLM (si es que seleccionó un servicio pago como fuente): ",
                                                        disabled=(controller.llm_origin not in PAID_SERVICE),
                                                        type='password')

    



if __name__ == "__main__":
    ConfigurationUI()