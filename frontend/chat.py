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
    if (len(query.strip()) > MINIMUM_CHARACTERS_PER_QUERY):
        response = Controller().answer_query(query)
        return response
    else:
        return None
    


def dynamic_printing(word):
    yield word


def set_button_information_source_fragments(context_docs, keywords, key_button):
    st.button("", key = key_button, 
              icon = ":material/quick_reference:",
              on_click = show_information_source_fragments, 
              args = [context_docs, keywords])



def ChatUI():
            
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


    expander_advanced_options = st.expander(label="Opciones Avanzadas")
    with expander_advanced_options:
        'XXXXXXXXXXXXXXXXXXXXX'
        clicked = st.button('Nada')


if __name__ == "__main__":
    ChatUI()




