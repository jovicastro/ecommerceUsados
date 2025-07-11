import requests
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

llm = Ollama(model="phi3:mini")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_store = None # A nossa "memória" do ebook

def setup_rag_chain():
    global vector_store

    try:
        # 1. Carregar o documento
        # IMPORTANTE: Use o caminho absoluto para o ficheiro ou garanta que o caminho relativo funciona a partir da raiz do projeto.
        loader = TextLoader("../ebooks/E-book Treinee MKT.pdf")
        docs = loader.load()

        # 2. Dividir o texto em pedaços (chunks)
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)

        # 3. Criar e armazenar os embeddings no Vector Store (FAISS)
        vector_store = FAISS.from_documents(documents, embeddings)
        print("✅ Sistema RAG (memória do ebook) carregado com sucesso!")

    except Exception as e:
        print(f"⚠️ AVISO: Não foi possível carregar o documento para o RAG: {e}")
        print("O chatbot funcionará no modo normal, sem conhecimento de ebooks.")

def get_rag_response(prompt_usuario: str) -> str:
    global vector_store

    if vector_store:
        prompt_template = ChatPromptTemplate.from_template("""
        Responda à pergunta do usuário em, Português Brasileiro, baseando-se apenas no contexto fornecido.
        Se a resposta não estiver no contexto, diga "Desculpe, não tenho informação sobre isso no documento."

        Contexto:
        {context}

        Pergunta: {input}
        """)

        document_chain = create_stuff_documents_chain(llm, prompt_template)
        retriever = vector_store.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({"input": prompt_usuario})
        return response.get("answer", "Não consegui gerar uma resposta.")

    # Fallback: Se o RAG não estiver configurado, funciona no modo normal
    else:
        payload = { "model": "phi3:mini", "prompt": prompt_usuario, "stream": False }
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        ollama_data = response.json()
        return ollama_data.get('response', "Não consegui gerar uma resposta.")