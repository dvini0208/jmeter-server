FROM python:3.11-slim

# Install Java (required for JMeter)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-jre-headless \
        curl \
        unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Apache JMeter
ENV JMETER_VERSION=5.6.3
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:${PATH}

RUN curl -fsSL https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.zip -o /tmp/jmeter.zip && \
    unzip -q /tmp/jmeter.zip -d /opt && \
    rm /tmp/jmeter.zip

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p storage/scripts storage/runs

# Expose port
EXPOSE 10000

# Set environment variables
ENV APP_JMETER_CMD=jmeter
ENV DATABASE_URL=sqlite:///./jmeter_ai.db
ENV STORAGE_ROOT=./storage

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
