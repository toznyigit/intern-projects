FROM python:3.8

COPY ./cagri.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev

RUN pip3 install --upgrade pip --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt 
RUN pip3 install --upgrade wheel --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt 
RUN pip3 install --upgrade setuptools --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt 

RUN pip3 install flask --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt
RUN pip3 install psycopg2 --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt
RUN pip3 install python-dotenv --trusted-host files.pythonhosted.org --cert /usr/local/share/ca-certificates/cagri.crt

COPY ./bare_server /app

WORKDIR /app

CMD flask run --host=0.0.0.0 --port=$FLASK_PORT
