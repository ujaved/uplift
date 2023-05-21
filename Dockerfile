FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server/ .
ENV FLASK_APP='server'
CMD [ "flask", "run", "--host", "172.17.0.2"]