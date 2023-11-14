FROM python:3.11.1-slim

WORKDIR ../../app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN ls

COPY ./docker/api/requirements.txt .
RUN apt-get update
RUN apt-get upgrade --yes
RUN apt-get install --yes libpq-dev


RUN pip install -r requirements.txt
RUN pip install alembic
RUN  #pip install "git+git://github.com/samuelcolvin/pydantic@master#egg=pydantic[email,typing_extensions]"
COPY . .
EXPOSE 8000
# CMD alembic -c /app/alembic.ini upgrade head
CMD uvicorn CS-Backend/app:app_ --reload --host 0.0.0.0 && bash -c "alembic -c CS-Backend/app/alembic.ini upgrade head"
