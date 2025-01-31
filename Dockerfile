FROM python:3

RUN mkdir -p /opt/ssh-honeypot

WORKDIR /opt/ssh-honeypot

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY ./entrypoint.sh .
COPY ./honeypot.py .

ENTRYPOINT [ "./entrypoint.sh" ]