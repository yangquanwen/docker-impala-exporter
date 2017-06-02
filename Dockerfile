FROM golang:1.7

WORKDIR /go/src/app
COPY generate_config.py .
RUN apt update
RUN apt install -y python-yaml 
RUN go-wrapper download github.com/kawamuray/prometheus-json-exporter
RUN go-wrapper install github.com/kawamuray/prometheus-json-exporter
ENV JSON_URI="http://localhost:25000/metrics?json"
RUN python generate_config.py "$JSON_URI" > json-config.yaml
CMD /go/bin/prometheus-json-exporter "$JSON_URI" ./json-config.yaml

