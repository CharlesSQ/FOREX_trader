# FXCM_trader

## Run with Docker

1. Install docker

```
sudo apt-get install docker.io
```

2. Create network

```
docker network create my_net
```

3. Run IB Gateway

```
docker run -d --env IB_ACCOUNT=charlesjsq --env IB_PASSWORD=LA@q7Pn*CFV-_vg --env TRADE_MODE=paper --network=my_net --name ib_gateway -p 4002:4002 charlessq/ib-gateway-ibc:v1.2 tail -f /dev/null
```

4. Run trader-bot

```
docker run -d --network=my_net --name trader-bot charlessq/trader_bot:v1.1.2
```
