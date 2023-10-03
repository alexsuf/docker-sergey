FROM jupyter/all-spark-notebook
# docker build . -t spark

USER root

RUN apt update
RUN apt install mc -y

COPY  requirements.txt .
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt