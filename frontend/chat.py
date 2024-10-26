from typing import List
import streamlit as st
from langchain_core.documents import Document
from backend.consultant_controller import ConsultantController as Controller


MINIMUM_CHARACTERS_PER_QUERY = 8


def show_information_source_fragments(context_docs:List[Document], keywords:str):
    
    sidebar_documents = st.sidebar

    with sidebar_documents:
        st.title("Fragmentos de documentación empleados para la respuesta:")
        for document in context_docs:

            st.write(f"Nombre del documento: **{document.metadata['source']}**")

            if "page" in document.metadata.keys():
                st.write(f"Número aproximado de página: **{document.metadata['page']}**")

            with st.container(border=True):
                st.write(f"Nombre del documento: **{document.metadata['source']}**")
                st.write(document.page_content)

        st.header("Palabras clave empleadas en la búsqueda de la base de datos: ")
        st.write(keywords)

    if (st.session_state.sidebar_state == 'collapsed'):
        st.session_state.sidebar_state = 'expanded'


def response_generator(query:str):
    response = Controller().answer_query(query)
    return response
     

def dynamic_printing(word):
    yield word


def set_button_information_source_fragments(context_docs, keywords, key_button):
    st.button("", key = key_button, 
              icon = ":material/quick_reference:",
              on_click = show_information_source_fragments, 
              args = [context_docs, keywords])


def chat_node():
    
    container_chat = st.container(border=True, height=500)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with container_chat.chat_message(message["role"]):
            col1, col2 = st.columns([8, 1])    
            if (message["role"] == "assistant"):
                content = message["content"]
                col1.markdown(content["output"])
                with col2:
                    set_button_information_source_fragments(content["context_docs"],
                                                            content["keywords"],
                                                            message["id"])
            else:
                col1.markdown(message["content"])
                

    # Accept user input
    if prompt := st.chat_input("Que desea consultar?"):

        if (len(prompt.strip()) <= MINIMUM_CHARACTERS_PER_QUERY):
            st.error(f'Error: la consulta debe tener un mínimo de {MINIMUM_CHARACTERS_PER_QUERY} caracteres.  ', icon="🚨")
            return None
    
        if not Controller().is_system_configured():
            st.error('Error: el sistema aun no se encuentra preparado para realizar la consulta. \nPor favor revise si se configuraron los recursos pertinentes.', icon="🚨")
            return None

        message_user = {"role": "user", 
                        "content": prompt,
                        "id": len(st.session_state.messages)}
        
        # Add user message to chat history
        st.session_state.messages.append(message_user)
        
        # Display user message in chat message container
        with container_chat.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with container_chat.chat_message("assistant"):
            col1, col2 = st.columns([8, 1])
            response = response_generator(prompt)
            col1.write_stream(dynamic_printing(response["output"]))
            with col2:
                key = len(st.session_state.messages)
                set_button_information_source_fragments(response["context_docs"], 
                                                        response["keywords"], key)
            
        # Add assistant response to chat history
        message_assistant = {"role": "assistant", 
                             "content": response, 
                             "id": len(st.session_state.messages)}
        st.session_state.messages.append(message_assistant)


def advanced_options_node():

    with st.expander(label="Opciones Avanzadas"):

        enter_keywords_manually = Controller().enter_keywords_manually = st.toggle("Introducir manualmente las palabras clave para la búsqueda del proceso de RAG")
        if (enter_keywords_manually):
            Controller().keywords = st.text_input(label="Introduzca la lista de palabras clave (separadas por una coma) para la búsqueda del RAG: ")

        Controller().optimized_database_query_enabled = st.toggle("Habilitar optimización del RAG por medio de Reranking (puede aumentar el tiempo de respuesta)")

        collection_filter = st.toggle("Filtrar la búsqueda del proceso de RAG por las colecciones de la base de datos")
        if collection_filter:
            collection_names_list = [collection.name for collection in Controller().database_manager.get_list_collections()]
            st.selectbox(label="Seleccione la colección por la que desea filtrar la búsqueda:",
                                                  options=collection_names_list)
                
        Controller().k_index = st.number_input(label="Introduzca el indice K: ", 
                                               max_value=10, min_value=1, value=3)


def ChatUI():
    chat_node()
    advanced_options_node()
            

if __name__ == "__main__":
    ChatUI()




