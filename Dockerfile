FROM python:3.8-slim-buster AS base
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


FROM base as test
COPY . .
WORKDIR /app/newsaggregate
CMD [ "python3", "-m", "unittest"]


FROM base as ml-base
RUN pip3 install torch==1.9.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install torchvision==0.10.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install sentence_transformers
COPY model_setup.py model_setup.py
RUN python3 model_setup.py





FROM ml-base as srv
COPY . .
WORKDIR /app/newsaggregate
CMD [ "python3", "-u", "-m", "recommend.main"]




FROM ml-base as lit
COPY . .
WORKDIR /app/newsaggregate
CMD [ "streamlit", "run", "test/lit2.py"]

FROM ml-base as ml
COPY . .
WORKDIR /app/newsaggregate
CMD [ "python3", "-u", "-m", "main"]


# FROM base as final
# COPY . .
# WORKDIR /app/newsaggregate
# CMD [ "python3", "-u", "-m", "main"]


