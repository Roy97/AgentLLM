FROM python:3.12.7
WORKDIR /app
COPY requirements.txt /app/
COPY main.py /app/
COPY agent_llm.py /app/
RUN pip install -r requirements.txt
EXPOSE 8001
ENTRYPOINT ["flet", "run", "--web"]