# Use official Python slim image for smaller size
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies including ffmpeg, gnupg, and curl properly
RUN apt-get update && \
    apt-get install -y ffmpeg gnupg curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS version) from official NodeSource repository
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt if you have one; otherwise create one with your dependencies
COPY requirements.txt .

# Install Python dependencies without cache to reduce layer size
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code into the working directory
COPY . .

# Expose the port where Streamlit runs
EXPOSE 8501

# Run Streamlit app in headless mode accessible on all network interfaces and port 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
