import streamlit as st


def response_generator(word):
    yield word + "xxx"


def chat():

    container_chat = st.container(border=True, height=500)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with container_chat.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Que desea consultar?"):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with container_chat.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with container_chat.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt))

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    chat()


