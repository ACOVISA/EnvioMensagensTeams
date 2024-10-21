# Use the official Azure Functions base image for Python
FROM mcr.microsoft.com/azure-functions/python:4-python3.11-slim

# Install any needed packages specified in requirements.txt
COPY requirements.txt /
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /home/site/wwwroot

RUN apt-get update && \
    apt-get install -y --no-install-recommends azure-functions-core-tools-4

# Expose the port Azure Functions runtime listens to
EXPOSE 80

WORKDIR /home/site/wwwroot

CMD ["func", "start", "--python"]