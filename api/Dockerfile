FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

COPY /app/ /app/
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app/server:api", "--host", "0.0.0.0", "--port", "8000"]