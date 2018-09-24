FROM python:3

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"config.settings.prod"}

RUN groupadd django
RUN useradd -g django django

RUN apt-get update

RUN apt-get install -y postgresql-client
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir /app
COPY . /app/

RUN chown -R django /app

WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

USER django

EXPOSE 8000

CMD chmod +x /app/config/django/cmd.sh && /app/config/django/cmd.sh
