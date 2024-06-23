# Use the latest OPAL client image as the base image
FROM permitio/opal-client:latest

# Set the working directory inside the container
WORKDIR /app/

# Copy the current directory contents into the container at /app/
COPY . /app/

# Install the required Python packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install the application
RUN cd /app && python setup.py install --user

# Set the default command to run the application
CMD ["./start.sh"]
