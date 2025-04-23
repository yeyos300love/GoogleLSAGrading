FROM selenium/standalone-chrome:114.0

USER root

# set the working directory inside the container
WORKDIR /app

# Remove any existing Python installations first
RUN apt-get update && \
    apt-get remove -y python3 python3-pip python3-dev && \
    apt-get autoremove -y && \
    rm -rf /usr/lib/python* /usr/local/lib/python*

# Install Python 3.8 and build dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-distutils \
    build-essential gcc g++ gfortran libopenblas-dev liblapack-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Verify Python version
RUN python --version && pip --version

COPY requirements.txt .
# install dependencies
RUN pip install --no-cache-dir setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create 2fa_code.json with initial value
RUN echo '{"code": "000000"}' > /app/2fa_code.json && \
    chown seluser:seluser /app/2fa_code.json

USER seluser

# expose the port that Flask will run on
EXPOSE 8080

# run the application
CMD ["python", "app.py"]