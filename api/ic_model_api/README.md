To run server, navigate to this folder and run:
```
export HF_TOKEN="your HuggingFace token for reading the indexing_api_store dataset from the AIMLOps-C4-G16 organisation"
uvicorn main:app --host 0.0.0.0 --port 8000 &>/content/logs.txt &
```

All the endpoints listed in the [API specs](https://github.com/AIMLOps-C4-G16/aimlops-capstone-project/wiki/Backend-Model-API-Specs) have been implemented. There are also additional html-returning endpoints with the format `/*_page` that can be used as a simple UI to study the functionality of the associated non-html-returning endpoints. Please see `/docs` for documentation of all the endpoints.

To forward the API via a tunnel, you can install and use localtunnel like this:
```
npm install localtunnel
curl https://loca.lt/mytunnelpassword
npx localtunnel --port 8000
```
