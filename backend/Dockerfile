FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

# Install CPU-only PyTorch first so sentence-transformers
# does not download NVIDIA/CUDA libraries.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]