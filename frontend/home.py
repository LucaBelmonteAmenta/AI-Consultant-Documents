from time import sleep
from typing import Tuple

import streamlit as st

from frontend.chat import ChatUI
from frontend.configuration import ConfigurationUI
from frontend.database_explorer import DatabaseExplorerUI
from frontend.fqa_and_help import FrequentlyAskedQuestionsUI


from backend.consultant_controller import ConsultantController as Controller
from backend.embedding_models import EmbeddingModelsManager, get_list_of_installed_embedding_names_models
from backend.vector_database import VectorDatabaseManager






class Home():

    def __init__(self) -> None:

        # Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
        if 'sidebar_state' not in st.session_state:
            st.session_state.sidebar_state = 'collapsed'

        controller = Controller()

        st.set_page_config(
            page_title="AI Consultant Documents",
            page_icon="🤖",
            layout="centered",
            initial_sidebar_state=st.session_state.sidebar_state,
            menu_items={
                'Get Help': 'https://aistudio.google.com/',
                'Report a bug': 'https://openai.com/index/openai-api/',
                'About': "# This is a header. This is an *extremely* cool app!"
            }
        )

        if not controller.init:
            embedding_manager, database_manager = self.set_up_system()
            controller.embedding_manager = embedding_manager
            controller.database_manager = database_manager
            controller.init = True


    def set_up_system(self) -> Tuple[EmbeddingModelsManager, VectorDatabaseManager]:
        
        placeholder = st.empty()

        with placeholder:
            
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
                database_manager = VectorDatabaseManager(embedding_models_manager.main_model)
                
                status.update(
                    label="System setup completed!", state="complete", expanded=False
                )
        
        sleep(5)

        placeholder.empty()

        return (embedding_models_manager, database_manager)


    @st.dialog("Error")
    def popup_error(self, error:str):
        st.write(error)
        if st.button("Cerrar"):
            st.stop()


    def run(self):

        #try:
        
            tab1, tab2, tab3, tab4 = st.tabs(["▶️ Chat", "🗂️ Base de Datos", "⚙️ Configuración", "❔ Ayuda"])
            with tab1:
                st.header("Chat con inteligencia artificial")
                ChatUI()
            with tab2:
                st.header("Base de datos vectorial")
                DatabaseExplorerUI()
            with tab3:
                st.header("Configuración")
                ConfigurationUI()
            with tab4:
                st.header("Preguntas frecuentes")
                FrequentlyAskedQuestionsUI()
                
         #except Exception as error:
             #self.popup_error(str(error))
             #print(error)

