# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- NEW STEPS TO PRE-DOWNLOAD THE MODEL ---
# Copy the new download script into the container
COPY download_model.py .
# Run the script. This will download the model during the build process.
RUN python download_model.py
# -------------------------------------------

# Copy the rest of the application code into the container
COPY . .

# Run main.py when the container launches
CMD ["python", "main.py"]