FROM python:3.8-alpine  

RUN mkdir /api
WORKDIR /api

#Do not buffer stdout and do not write bytecode to disk

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#copy project:
COPY . .

COPY ./entrypoint.sh /usr/local/bin
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


# run entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

