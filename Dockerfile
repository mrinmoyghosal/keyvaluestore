FROM python:3.7
COPY . /app
WORKDIR /app
ENV PYTHONPATH /app/
RUN pip install pipenv
RUN pipenv install --system
RUN ["py.test"]