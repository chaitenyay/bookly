
FROM python:3.14

WORKDIR /code

# Install system dependencies (needed for healthcheck + pg_isready)
RUN apt-get update && apt-get install -y curl postgresql-client && rm -rf /var/lib/apt/lists/*

# For Production:
# COPY . .

# For Development: Copy only necessary files to speed up build and enable caching of dependencies
COPY requirements.txt .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT ["/code/entrypoint.sh"]
