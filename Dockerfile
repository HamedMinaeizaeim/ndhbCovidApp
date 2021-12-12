FROM heroku/miniconda

# Grab requirements.txt.
ADD requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt

# Add our code
#ADD ./webapp /opt/webapp/
#WORKDIR /opt/webapp

RUN conda install 
RUN    conda install pandas fiona shapely pyproj rtree
RUN    conda install geopandas
RUN    conda update --all --yes

#CMD gunicorn --bind 0.0.0.0:$PORT wsgi