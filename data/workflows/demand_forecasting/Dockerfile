FROM python:3.12-slim

WORKDIR /pipeline

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#COPY data/ /pipeline/data/
COPY scripts/ /pipeline/scripts/

ENTRYPOINT ["python"]
