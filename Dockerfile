# Use Python 3.9 slim buster image
FROM python:3.10-slim-buster

# This was nessessary to get the ODBC driver working on our other project so may need it for this.
# # Install system dependencies for PyODBC
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         gnupg \
#         g++ \
#         unixodbc-dev \
#         curl

# # Add Microsoft repository key
# RUN curl https://packages.microsoft.com/keys/microsoft.asc -o microsoft.asc \
#     && apt-key add microsoft.asc

# # Add Microsoft repository for Debian 10 (Buster)
# RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list

# # Install msodbcsql17
# RUN apt-get update \
#     && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18

# # Clean up
# RUN apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Run server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]