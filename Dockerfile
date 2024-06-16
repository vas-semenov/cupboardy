# NOTE name need to be Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD [ "flask", "--app", "app", "run","--host=0.0.0.0", "--port=4000"]