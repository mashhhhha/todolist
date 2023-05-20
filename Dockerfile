FROM python:3.10.7-slim

ENV POETRY_VERSION=1.4.2
RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /opt
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root
    
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#
#COPY requirements.txt .
#RUN pip install -r requirements.txt \
#    && pip install gunicorn    
    
    

COPY . .

ENTRYPOINT ["bash", "entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "todolist.wsgi", "-w", "4", "-b", "0.0.0.0:8000"]


#папка env 
#DB_NAME=todolist_db
#DB_USER=todolist_admin
#DB_PASSWORD=todolist_password



