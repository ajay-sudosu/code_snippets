#### 1.Schedule the api server
```shell
export ENV=DEV
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
pm2 --name=backend-api start 'uvicorn main:app --host 0.0.0.0 --port 5039'
```

With DataDog integration

```shell
pm2 --name=backend-api start 'DD_SERVICE="backend-api" DD_ENV="dev" DD_LOGS_INJECTION=true DD_PROFILING_ENABLED=true ddtrace-run uvicorn main:app --host 0.0.0.0 --port 5039'
```
