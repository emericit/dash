FROM python:3.9-alpine

# il faut un compilateur fortran pour numpy
RUN apk add make cmake gcc g++ gfortran blas lapack musl-dev linux-headers
# Create a directory where the code is to be hosted
RUN mkdir /app
# Define the working directory in the container
WORKDIR /app 
# Copy and install the requirements.
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
# Copy application code to the image
COPY . /app/

# Define environment variables
ENV DASH_PORT=8080
EXPOSE $DASH_PORT

CMD ["python", "main.py"]