FROM python:3.10.2

ADD webscraping_webmotors.py .
ADD requirements.txt .
ADD config.ini .
RUN pip install -r requirements.txt

CMD ["python", "./webscraping_webmotors.py"]