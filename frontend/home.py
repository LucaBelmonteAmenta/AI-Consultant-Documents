from config import init

from time import sleep

import streamlit as st

from frontend.chat import ChatUI
from frontend.configuration import ConfigurationUI
from frontend.database_explorer import database_explorer

from backend.main_controller import Controller
from backend.embedding_models import EmbeddingModelsManager, get_list_of_installed_embedding_names_models
from backend.vector_database import VectorDatabaseManager






class Home():

    def __init__(self) -> None:

        if not Controller().init:

            st.set_page_config(
                page_title="AI Consultant Documents",
                page_icon="🤖",
                layout="centered",
                initial_sidebar_state="collapsed",
                menu_items={
                    'Get Help': 'https://www.google.com/',
                    'Report a bug': "https://www.google.com/",
                    'About': "# This is a header. This is an *extremely* cool app!"
                }
            )
            
            self.set_up_system()
 
            Controller().init = True


    def set_up_system(self):
        
        with st.empty():

            with st.status("Setting up system...", expanded=True) as status:
                
                sleep(4)
                st.write("Checking for the existence of installed embedding models")
                list_embedding_models = get_list_of_installed_embedding_names_models()
                number_of_embedding_models = len(list_embedding_models)

                if (number_of_embedding_models > 0):
                    st.write(f"Confirmed the presence of {number_of_embedding_models} embedding models installed in the system")
                    embedding_models_manager = EmbeddingModelsManager(setup_local_models=False)
                else:
                    st.write("Downloading and installing embedding models")
                    embedding_models_manager = EmbeddingModelsManager(setup_local_models=True)

                st.write("Building vector database")
                VectorDatabaseManager(embedding_models_manager.main_model)

                status.update(
                    label="System setup completed!", state="complete", expanded=False
                )


    @st.dialog("Error")
    def popup_error(self, error:str):
        st.write(error)
        if st.button("Cerrar"):
            st.stop()


    def run(self):

        try:
            tab1, tab2, tab3 = st.tabs(["▶️ Chat", "🗂️ Base de Datos", "⚙️ Configuración"])
            with tab1:
                st.header("Chat con inteligencia artificial")
                ChatUI()
            with tab2:
                st.header("Base de datos vectorial")
                database_explorer()
            with tab3:
                st.header("Configuración")
                ConfigurationUI()
        except Exception as error:
            self.popup_error(str(error))

