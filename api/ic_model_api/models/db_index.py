import base64
import tempfile

import chromadb
from chromadb.config import Settings
from fastapi import HTTPException
from huggingface_hub import HfApi, hf_hub_download


HF_STORE = "AIMLOps-C4-G16/indexing_api_store"
NUM_IMAGES = 10


class ImageDatabaseIndex:


    def __init__(self, ic_model, hf_token):
        try:
            self.db_client = chromadb.Client(Settings(anonymized_telemetry=False))
            self.collection = self.db_client.create_collection(name="flicker8k")
            self.ic_model = ic_model
            self.hf_token = hf_token

            self.hf_api = HfApi(token=self.hf_token)
            info = self.hf_api.dataset_info(HF_STORE)

            self.status = ""

            with tempfile.TemporaryDirectory() as tmpdir:
                ids, docs = [], []

                for f in info.siblings[1::len(info.siblings)//NUM_IMAGES]:
                    img_file = hf_hub_download(
                        repo_id=HF_STORE,
                        filename=f.rfilename,
                        repo_type="dataset",
                        cache_dir=tmpdir,
                        local_dir_use_symlinks=False,
                        token=hf_token
                    )

                    caption = self.ic_model.caption(img_file)

                    ids.append(f.rfilename)
                    docs.append(caption)

                self.collection.add(ids=ids, documents=docs)

            self.status = "Successfully indexed image database"

        except Exception as e:
            self.status = "Unable to index image database: " + str(e)


    def search(self, text: str, num: int):
        if self.status != "Successfully indexed image database":
            return self.status

        try:
            ids = self.collection.query(query_texts=[text], n_results=num)['ids'][0]

            images_data = []
            with tempfile.TemporaryDirectory() as tmpdir:
                for f in ids:
                    img_file = hf_hub_download(
                        repo_id=HF_STORE,
                        filename=f,
                        repo_type="dataset",
                        cache_dir=tmpdir,
                        local_dir_use_symlinks=False,
                        token=self.hf_token
                    )

                    with open(img_file, mode='rb') as _file:
                        data = _file.read()
                        images_data.append(base64.b64encode(data).decode("utf-8"))

            return [images_data]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
