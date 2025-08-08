FROM alpine:3.20

RUN apk add --no-cache bash curl

# Install Supercronic
RUN curl -fsSLO "https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64" \
    && chmod +x supercronic-linux-amd64 \
    && mv supercronic-linux-amd64 /usr/bin/supercronic \
    && /usr/bin/supercronic -version

WORKDIR /app

# Copy crontab to a fixed path
COPY crontab /etc/crontab
RUN chmod 0644 /etc/crontab

# Copy script
COPY script.sh /app/script.sh
RUN chmod +x /app/script.sh

# Use ENTRYPOINT + CMD
ENTRYPOINT ["/usr/bin/supercronic"]
CMD ["/etc/crontab"]
