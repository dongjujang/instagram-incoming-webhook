FROM ghmlee/python

ADD . /instagram-incoming-webhook
RUN pip install -r /instagram-incoming-webhook/requirements.txt

WORKDIR /instagram-incoming-webhook

EXPOSE 8888

CMD python app.py