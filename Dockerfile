FROM python:3.10

# WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir /api
COPY ./ /
EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]