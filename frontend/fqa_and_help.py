import streamlit as st

k_explanation_text = """
K: número de fragmentos de documento de la base de datos que es extraído por el LLM por cada consulta, como fuente de información para responder a la misma.\n
Mientas más fragmentos de documentos emplee el modelo, mas tokens consumirá la respectiva consulta realizada. Tome esto en cuenta si emplea un servicio pago para el LLM, o si el mismo posee un límite máximo de tokens por consulta.\n
Tome en cuenta que, a mayor K también aumenta la probabilidad de que uno de los fragmentos extraídos posea la información necesaria para responder a la consulta realizada, pero a la vez aumenta la probabilidad de alucinaciones en la respuesta por parte del LLM.
"""

reranking_explanation_text = """
Reranking: implica reevaluar y reorganizar los documentos o datos recuperados en función de su relevancia para la consulta. Este proceso perfecciona los resultados de la recuperación al priorizar aquellos documentos que son más apropiados en términos de contexto para la consulta. Esta selección mejorada mejora la calidad y precisión general de la información que el modelo utiliza para generar su salida final.
En el ámbito del procesamiento avanzado del lenguaje, el reranking emerge como una técnica fundamental que eleva el rendimiento de los modelos RAG. 
"""

llm_explanation_text = """
LLM: (Large Language Model) es un modelo de inteligencia artificial basado en redes neuronales profundas, diseñado para procesar y generar texto natural. Entrenado con grandes volúmenes de datos textuales, un LLM aprende patrones del lenguaje, lo que le permite realizar tareas como responder preguntas, completar frases, generar contenido coherente y mantener conversaciones. Estos modelos son altamente efectivos en la comprensión del contexto y la producción de lenguaje humano, siendo utilizados en aplicaciones como chatbots, generación automática de texto y análisis de datos lingüísticos.
"""

rag_explanation_text = """
RAG: (Retrieval-Augmented Generation) es un enfoque en inteligencia artificial que combina la generación de lenguaje natural con la recuperación de información de fuentes externas. Funciona en dos fases: primero, el modelo recupera datos relevantes de una base de conocimiento o un conjunto de documentos (como bases de datos o internet), y luego utiliza esos datos para generar respuestas o contenido contextualizado.
A diferencia de los modelos puramente generativos, un RAG mejora la precisión y relevancia de las respuestas al apoyarse en información actualizada y específica, lo que lo hace útil para tareas que requieren acceso a conocimiento más allá del contenido aprendido durante el entrenamiento del modelo.
"""


def FrequentlyAskedQuestionsUI():
    
    with st.expander("Que significa K?"):
        st.write(k_explanation_text)

    with st.expander("Que significa Reranking?"):
        st.write(reranking_explanation_text)

    with st.expander("Que significa LLM?"):
        st.write(llm_explanation_text)

    with st.expander("Que significa RAG?"):
        st.write(rag_explanation_text)
    