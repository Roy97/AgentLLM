FROM python:3.12.7
WORKDIR /app
COPY requirements.txt /app/
COPY main.py /app/
COPY agent_llm.py /app/
ENV FLET_SECRET_KEY="secret_file_upload_key"
RUN pip install --upgrade pip
RUN pip install "langchain-unstructured[pdf]"
RUN pip install -r requirements.txt
EXPOSE 8001
ENTRYPOINT ["flet", "run", "--web", "--port", "8001"]