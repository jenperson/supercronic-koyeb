FROM alpine:3.20

# Install curl for health checks/logging and bash for scripting
RUN apk add --no-cache bash curl

# Download Supercronic
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64

RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" /usr/local/bin/supercronic \
    && supercronic -version  # <-- Adding temporarily to confirm it works at build time


# Set work directory
WORKDIR /app

# Copy files
COPY crontab /app/crontab
COPY script.sh /app/script.sh

# Ensure script is executable
RUN chmod +x /app/script.sh

# Command to run supercronic with our crontab
CMD ["supercronic", "-debug", "/app/crontab"]
