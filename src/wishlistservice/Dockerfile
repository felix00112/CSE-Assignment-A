FROM python:3.13.1-slim as base

FROM base AS builder

# Install pip-tools
RUN pip install pip-tools

# Copy requirements.in and generate requirements.txt
COPY requirements.in .
RUN pip-compile requirements.in

# Install dependencies
RUN pip install -r requirements.txt

FROM base
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

WORKDIR /wishlist_service

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.13/ /usr/local/lib/python3.13/

# Add the application
COPY . .

EXPOSE 50052

ENTRYPOINT ["python", "src/wishlist_server.py"]