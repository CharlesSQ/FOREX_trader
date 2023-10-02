# Utilizamos la imagen oficial de Python 3.8
FROM python:3.8-slim

# Creamos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    wget

# Descargamos TA-Lib, lo compilamos desde la fuente e instalamos
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install

# Instalamos las librerías de Python necesarias
RUN pip3 install wheel==0.41.0
RUN pip3 install TA-Lib
RUN pip3 install ib_insync==0.9.86
RUN pip3 install pandas==2.0.3
RUN pip3 install plotly==5.15.0
RUN pip3 install python-dotenv==1.0.0
RUN pip3 install colorlog==6.7.0

# Copiamos el código del algoritmo al directorio de trabajo
COPY . /app

# Ejecutamos el código del algoritmo cuando se inicia el contenedor
CMD ["python3", "app.py"]
