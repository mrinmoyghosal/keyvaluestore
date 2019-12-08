## Build and Run without Docker (need to have redis running in local)

### Install Dependencies
```bash
sudo apt-get install python3 python3-pip
pip3 install pipenv
cd NiTask
pipenv install --system
```

### Run the server
```bash
export PYTHONPATH=$(pwd)
# configure redis url
export REDIS_URL=redis://redis:6379/0
python3 app/main.py
```

### Run tests
```bash
py.test
```

# Build with docker-compose
```bash
docker-compose up --build
```
### Swagger URL
visit the url for swagger documentations
```bash
http://localhost:5000/api
```

### Prometheus Metrics Endpoint
visit the following url for prometheus metrics
```bash
http://localhost:5000/metrics
```

### Todo
* Using redis ttl functionality for expire instead of APScheduler
* managing number of workers
* adding kubernetes deployment file
