# Use Python 3.12 base image
FROM python:3.12

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

# Command to run the application
CMD ["python", "src/app.py"]
