FROM tensorflow/tensorflow:1.15.2-gpu
RUN pip install bert-serving-server
COPY ./ /app
COPY ./entrypoint.sh /app
WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
