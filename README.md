# AgentLLM
## Setup instructions
- Download and install Ollama
- Pull the llama3.2 model
```console
ollama pull llama3.2
```
- Pull the nomic-embed-text model for text embeddings
```console
ollama pull nomic-embed-text
```
- Generate API keys for Unstructured and add as an environment variable
- Install package dependencies from requirements.txt
- Execute
```console
flet run
```
### To analyse images
- Install Tesseract-OCR
- Configure the PATH environment variable
