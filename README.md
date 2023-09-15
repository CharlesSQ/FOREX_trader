# FXCM_trader

## Install python 3.8.10

```
sudo apt install wget build-essential zlib1g-dev libnss3-dev libssl-dev libreadline-dev libncurses5-dev libffi-dev libgdbm-dev \
&& wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz \
&& tar -xf Python-3.8.10.tar.xz \
&& cd Python-3.8.10 \
&& ./configure --enable-optimizations \
&& make \
&& sudo make altinstall
```

## Install docker

```
sudo apt-get install docker.io
```

## Install github CLI and Login

```
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

```
sudo apt update
sudo apt install gh
```

```
gh auth login
```

## Clone repo

```
git clone https://github.com/CharlesSQ/FOREX_trader.git
```

## Install trader-bot dependencies

```
cd FOREX_trader \
&& apt-get update && apt-get install -y \
&& build-essential \
&& wget
```

```
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
&& tar -xvf ta-lib-0.4.0-src.tar.gz \
&& cd ta-lib/ \
&& ./configure --prefix=/usr \
&& make \
&& make install
```

```
pip3 install -r requirements.txt
```

## Run IB Gateway

```
docker run -d --env IB_ACCOUNT=charlesjsq --env IB_PASSWORD=LA@q7Pn\*CFV-\_vg --env TRADE_MODE=paper -p 4002:4002 charlessq/ib-gateway-ibc:v1.2 tail -f /dev/null
```

## Run trader-bot

```
python3.8 FOREX_trader/app.py
```
