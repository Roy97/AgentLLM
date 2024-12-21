FROM python:3.12.7
WORKDIR /app
COPY requirements.txt /app/
COPY main.py /app/
COPY agent_llm.py /app/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && export PATH="$HOME/.cargo/bin:$PATH" \
    && rustup install stable \
    && rustup default stable \
    && rustup update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8001
ENTRYPOINT ["flet", "run", "--web"]