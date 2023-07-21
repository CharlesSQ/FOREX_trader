# Utilizamos la imagen oficial de Python 3.8
FROM python:3.8-slim

# Creamos el directorio de trabajo
WORKDIR /app

# Copiamos el código del algoritmo al directorio de trabajo
COPY . /app

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
    && sudo make install

# Instalamos las librerías de Python necesarias
RUN pip3 install wheel ib_insync numpy pandas TA-Lib

# Ejecutamos el código del algoritmo cuando se inicia el contenedor
CMD ["python3", "trading_bot.py"]
