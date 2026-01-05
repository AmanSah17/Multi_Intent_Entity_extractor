# Ollama Setup Guide

## Install Ollama

### Windows
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

### Verify Installation
```bash
ollama --version
```

## Pull a Model

### Recommended Models

**Llama 3 (Best for this task):**
```bash
ollama pull llama3
```

**Alternatives:**
```bash
# Smaller, faster
ollama pull llama2

# Good for structured output
ollama pull mistral

# Very small, fast
ollama pull phi3
```

## Test Ollama

```bash
ollama run llama3 "Hello, how are you?"
```

## Update Requirements

Add to `requirements.txt`:
```
langchain-community>=0.0.20
```

Install:
```bash
pip install langchain-community
```

## Restart Services

After installing Ollama and pulling a model:

```bash
# Stop current server (Ctrl+C)
# Then restart:
cd agentic_pipeline
python api_server.py
```

## Model Selection

Edit `config/settings.py` to change model:
```python
local_llm_model: str = "llama3"  # or "llama2", "mistral", "phi3"
```

## Troubleshooting

### Ollama not found
- Make sure Ollama is installed and running
- Check: `ollama list` to see installed models

### Model not found
- Pull the model: `ollama pull llama3`
- Verify: `ollama list`

### Slow responses
- Use smaller model: `phi3` or `llama2`
- Ollama runs on CPU by default, GPU support available

## Performance

- **Llama 3**: Best quality, slower (~5-10s per query)
- **Mistral**: Good balance (~3-5s per query)
- **Phi3**: Fastest, smaller model (~1-3s per query)

Choose based on your hardware and speed requirements.
