# Use image with both python and node installed
FROM nikolaik/python-nodejs:python3.8-nodejs18

WORKDIR /app/server/

# Install Python dependencies
COPY ./moni-moni/server/requirements.txt /app/server/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install client dependencies
WORKDIR /app/client/

COPY ./moni-moni/client/package.json ./moni-moni/client/package-lock.json /app/client/
RUN npm install

# Add the rest of the code
COPY ./moni-moni /app/

# Build static files
RUN npm run build

# Move all static files other than index.html to root/ for whitenoise middleware
WORKDIR /app/client/build

RUN mkdir root && mv *.ico *.json root

# Collect static files
RUN mkdir /app/server/staticfiles

WORKDIR /app