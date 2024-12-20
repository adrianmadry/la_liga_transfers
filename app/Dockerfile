# Use a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the application's port (adjust based on your app)
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "dashboard_app.py"]