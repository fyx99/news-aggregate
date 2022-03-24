FROM python:3.8-slim-buster AS base
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


FROM base as test
COPY . .
CMD [ "python3", "-m", "unittest"]


FROM base as final
COPY . .
CMD [ "python3", "-u", "-m", "main"]


