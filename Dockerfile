FROM python:3.11-alpine

# Install Supercronic
RUN apk add --no-cache bash curl \
    && curl -fsSLO "https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64" \
    && chmod +x supercronic-linux-amd64 \
    && mv supercronic-linux-amd64 /usr/bin/supercronic \
    && /usr/bin/supercronic -version

WORKDIR /app

# Copy crontab to a fixed path
COPY crontab /etc/crontab
RUN chmod 0644 /etc/crontab

# Get the required pip packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy python app files
COPY ["*.py", "./"]

# Copy script
COPY script.sh ./script.sh
RUN chmod +x ./script.sh

# Use ENTRYPOINT + CMD
ENTRYPOINT ["/usr/bin/supercronic"]
CMD ["/etc/crontab"]
