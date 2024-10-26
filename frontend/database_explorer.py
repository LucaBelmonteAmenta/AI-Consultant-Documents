import streamlit as st

import pandas as pd





def DatabaseExplorerUI():

    col1, col2 = st.columns((1, 2))

    with col1:
        container_1 = st.container(border=True)
        container_1.write("hola")

    with col2:
        container_2 = st.container(border=True)
        container_2.write("hola")



    

    

if __name__ == "__main__":
    DatabaseExplorerUI()


