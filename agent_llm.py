import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import MemorySaver
from langchain_unstructured import UnstructuredLoader
from langchain_ai21 import AI21SemanticTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL

from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent

class AgentLLM:

    def __init__(self):
        os.environ["UNSTRUCTURED_API_KEY"] = "Ifx4J2RRTUaCYXALmRcoH1ucCr70Pd"
        os.environ["AI21_API_KEY"] = "VXgSDh46P4UWXyTXpF0PNNedEYgl9rdZ"

        self.llm = ChatOllama(model="llama3.2", base_url="http://ollama:80")
        self.memory = MemorySaver()
        self.agent_store = Chroma()
        self.agent = None
        self.chat_history = []
        self.agent_scratchpad = []
        python_repl = PythonREPL()
        self.code_tool = Tool(
            name="python_repl",
            description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
            func=python_repl.run
        )
    
    def RAG(self, doc_path=None):
        if doc_path:
            loader = UnstructuredLoader(doc_path)
            docs = loader.load()
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            compressor = FlashrankRerank()
            ai21_sts = AI21SemanticTextSplitter(chunk_size=10000, chunk_overlap=2000)
            for i in docs:
                if len(i.page_content) < 30:
                    i.page_content = i.page_content + " " * (30 - len(i.page_content))
            split_docs = ai21_sts.split_documents(docs)
            filter_docs = filter_complex_metadata(split_docs, allowed_types=(str, bool, int, float))
            vector_store = Chroma.from_documents(filter_docs, embeddings)
            retriever = vector_store.as_retriever(search_type = "mmr", k=10)
            cc_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

            system_prompt = [
                ("system", "You are an assistant for question-answering tasks."
                            "Answer the following questions as best you can."
                            "You have access to the chat history (use it to answer questions related to past conversations)."
                            "You have access to tools (use it only when the question matches the tool description)."
                            "Provide long answers with proper formatting and detailed analysis."
                            "If you don't know the answer, just say that you don't know."
                            ),
                ("placeholder", "{messages}"),
                ("placeholder", "{chat_history}"),
                ("placeholder", "{agent_scratchpad}")
            ]

            prompt = ChatPromptTemplate.from_messages(system_prompt)
            doc_tool = create_retriever_tool(cc_retriever, "document_retriever", "Searches, analyses, and returns relevant information from the document based on the user's question")
            self.agent = create_react_agent(self.llm, [doc_tool, self.code_tool], state_modifier=prompt, checkpointer=self.memory, store=self.agent_store)
        else:
            system_prompt = [
                ("system", "You are a helpful and friendly assistant for question-answering tasks."
                            "Answer the following questions as best you can."
                            "You have access to the chat history (use it to answer questions related to past conversations)."
                            "You have access to a tool (use it only when the question matches the tool description)."
                            "Provide detailed answers with proper formatting."
                            "If you don't know the answer, just say that you don't know."
                            ),
                ("placeholder", "{messages}"),
                ("placeholder", "{chat_history}"),
                ("placeholder", "{agent_scratchpad}")
            ]

            prompt = ChatPromptTemplate.from_messages(system_prompt)
            self.agent = create_react_agent(self.llm, [self.code_tool], state_modifier=prompt, checkpointer=self.memory, store=self.agent_store)
            #chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    
    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def conversation(self, query):
        #print("Enter query:")
        #query = input()
        #result = chain.invoke(query)
        #print("\n", result)
        human_message = None
        ai_message = None
        for event in self.agent.stream(
            {"messages": [HumanMessage(content=query)], "chat_history": self.chat_history, "agent_scratchpad": self.agent_scratchpad},
            config={"configurable": {"thread_id": "rag0"}},
            stream_mode="values",
            ):
            for message in event["messages"]:
                if isinstance(message, HumanMessage):
                    human_message = message
                elif isinstance(message, AIMessage):
                    ai_message = message
                elif isinstance(message, ToolMessage):
                    self.agent_scratchpad.append(message)
        self.chat_history.append(human_message)
        self.chat_history.append(ai_message)
        return ai_message.content