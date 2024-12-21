FROM python:3.8.20
WORKDIR /app
COPY requirements.txt /app/
COPY main.py /app/
COPY agent_llm.py /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8001
ENTRYPOINT ["flet", "run", "--web"]