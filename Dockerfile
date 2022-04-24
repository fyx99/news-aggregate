FROM python:3.8-slim-buster AS base
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#RUN pip3 install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu


RUN pip3 install torch==1.9.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install torchvision==0.10.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN pip3 install sentence_transformers
COPY model_setup.py model_setup.py
RUN python3 model_setup.py


FROM base as test
COPY . .
CMD [ "python3", "-m", "unittest"]


FROM base as final
COPY . .
CMD [ "python3", "-u", "-m", "main"]


