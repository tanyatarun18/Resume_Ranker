# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install gunicorn, a production-ready web server for Flask
RUN pip install gunicorn

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8080 to the outside world so we can connect to it
EXPOSE 8080

# Run the gunicorn web server when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
