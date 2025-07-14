To run server, navigate to this folder and run:
```
export HF_TOKEN="your HuggingFace token for reading & writing datasets from the AIMLOps-C4-G16 organisation"
uvicorn main:app --host 0.0.0.0 --port 8000 &>/content/logs.txt &
```

Based on the [API specs](https://github.com/AIMLOps-C4-G16/aimlops-capstone-project/wiki/Backend-Model-API-Specs), all the endpoints except /index have been implemented as of now. Please see /docs for documentation of the endpoints.

To forward via a tunnel, you can install and use localtunnel like this:
```
npm install localtunnel
curl https://loca.lt/mytunnelpassword
npx localtunnel --port 8000
```