FROM python:3.9-slim

WORKDIR /data-drive
RUN mkdir -p attendance-data-reconciliation/files/config
RUN echo '{ \
  "logLevel": "DEBUG", \
  "acquisitionInterval": 60000, \
  "baseUrl": "http://127.0.0.1:2011" \
}' > attendance-data-reconciliation/files/config/config.json
RUN mkdir -p attendance-data-reconciliation/files/db
RUN mkdir -p attendance-data-reconciliation/logs

WORKDIR /attendance-data-reconciliation

COPY requirements.txt .

RUN echo 'from attendance_reconciliation.startup import start_attendance_reconciliation\nstart_attendance_reconciliation("PROD")' > start.py

RUN python3 -m venv randomenv
RUN . randomenv/bin/activate && pip3 install -r requirements.txt && pip3 install --upgrade pip

COPY ./src /attendance-data-reconciliation/randomenv/lib/python3.9/site-packages

EXPOSE 2011

CMD ["sh", "-c", ". randomenv/bin/activate && python start.py"]