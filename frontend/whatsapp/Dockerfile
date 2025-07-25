FROM python:3.12-slim

ADD whatsapp.py /whatsapp.py
ADD requirements.txt /requirements.txt

RUN mkdir images

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "whatsapp:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]