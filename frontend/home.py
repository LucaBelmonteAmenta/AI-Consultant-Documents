from config import init

from time import sleep

import streamlit as st

from frontend.chat import chat
from frontend.configuration import configuration
from frontend.database_explorer import database_explorer

from backend.embedding_models import EmbeddingModelsManager
from backend.vector_database import VectorDatabaseManager



class Home():

    def __init__(self) -> None:

        global init
        if init:
            
            with st.status("Setting up system...", expanded=True) as status:
                
                sleep(4)
                st.write("Checking for the existence of installed embedding models")
                list_embedding_models = EmbeddingModelsManager.get_list_of_installed_embedding_names_models()
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

                init = False

            st.empty()

        


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
                chat()
            with tab2:
                st.header("Base de datos vectorial")
                database_explorer()
            with tab3:
                st.header("Configuración")
                configuration()
        except Exception as error:
            self.popup_error(str(error))

