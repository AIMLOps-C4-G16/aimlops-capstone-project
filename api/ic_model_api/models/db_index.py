import base64
import os
import shutil
import tempfile

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from fastapi import HTTPException
from huggingface_hub import hf_hub_download


LOCAL_CHROMA_FOLDER = "chromadb"
HF_STORE = "AIMLOps-C4-G16/indexing_api_store"
ZIPPED_INDEX_FILEPATH = "chromadb_index.zip"


class ImageDatabaseIndex:


    def __init__(self, hf_token):
        try:
            self.hf_token = hf_token

            if not os.path.exists(LOCAL_CHROMA_FOLDER):
                os.makedirs(LOCAL_CHROMA_FOLDER)
            
            zipped_index_file = hf_hub_download(
                repo_id=HF_STORE,
                filename=ZIPPED_INDEX_FILEPATH,
                repo_type="dataset",
                cache_dir=LOCAL_CHROMA_FOLDER,
                local_dir_use_symlinks=False,
                token=self.hf_token
            )
            shutil.unpack_archive(zipped_index_file, LOCAL_CHROMA_FOLDER, 'zip')

            persist_directory = LOCAL_CHROMA_FOLDER + "/chromadb_index"
            self.db_client = chromadb.PersistentClient(path=persist_directory, settings=Settings(anonymized_telemetry=False))

            embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device="cuda")
            self.collection = self.db_client.get_or_create_collection(name="flicker8k", embedding_function=embedding_function)

            self.status = "Successfully loaded image database index"

        except Exception as e:
            self.status = "Unable to load image database index: " + str(e)


    def search(self, text: str, num: int):
        if self.status != "Successfully loaded image database index":
            raise HTTPException(status_code=500, detail=self.status)

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
