FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip -i https://pypi.python.org/simple
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Run migrations during the container startup (not during build)
#CMD ["python", "manage.py", "migrate"]

# Start the application with Gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
