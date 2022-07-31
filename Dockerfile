FROM python:3.8-slim-buster AS base
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt




FROM python:3.8-slim-buster AS ml-base
WORKDIR /app
RUN pip3 install torch==1.9.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install torchvision==0.10.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install sentence_transformers
COPY model_setup.py model_setup.py
RUN python3 model_setup.py

FROM ml-base AS ml-base-requirements
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


FROM ml-base-requirements as test
COPY . .
WORKDIR /app/newsaggregate
CMD [ "python3", "-m", "unittest"]


FROM ml-base-requirements as srv
COPY . .
WORKDIR /app/newsaggregate
CMD [ "python3", "-u", "-m", "recommend.main"]




FROM ml-base-requirements as lit
COPY . .
WORKDIR /app/newsaggregate
CMD [ "streamlit", "run", "test/lit2.py"]

FROM ml-base-requirements as RSS
COPY . .
WORKDIR /app/newsaggregate
ENV TASK=RSS
CMD [ "python3", "-u", "-m", "main"]


FROM ml-base-requirements as FEED
COPY . .
WORKDIR /app/newsaggregate
ENV TASK=FEED
CMD [ "python3", "-u", "-m", "main"]


FROM ml-base-requirements as REPROCESS_TEXT
COPY . .
WORKDIR /app/newsaggregate
ENV TASK=REPROCESS_TEXT
CMD [ "python3", "-u", "-m", "main"]



