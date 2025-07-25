FROM python:3.10.12-slim
WORKDIR /argus
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .
CMD ["python", "run_etls.py"]