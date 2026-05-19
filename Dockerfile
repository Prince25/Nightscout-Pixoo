# Use Python 3.13.5 base image
FROM python:3.13.5

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Initialize and update submodule
RUN git submodule update --init --recursive

# Install pip dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint to run the application
ENTRYPOINT ["python", "src/app.py"]
