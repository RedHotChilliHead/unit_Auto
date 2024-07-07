FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /unit_auto

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY unit_Avto .

CMD ["python", "manage.py", "runserver"]