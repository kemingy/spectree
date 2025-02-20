from enum import Enum
from random import random

from flask import Flask, abort, jsonify
from flask.views import MethodView
from pydantic import BaseModel, Field

from examples.common import File, FileResp, Query
from spectree import Response, SpecTree

app = Flask(__name__)
spec = SpecTree("flask")


class Resp(BaseModel):
    label: int
    score: float = Field(
        ...,
        gt=0,
        lt=1,
    )


class Data(BaseModel):
    uid: str
    limit: int = 5
    vip: bool

    class Config:
        schema_extra = {
            "example": {
                "uid": "very_important_user",
                "limit": 10,
                "vip": True,
            }
        }


class Language(str, Enum):
    en = "en-US"
    zh = "zh-CN"


class Header(BaseModel):
    Lang: Language


class Cookie(BaseModel):
    key: str


@app.route(
    "/api/predict/<string(length=2):source>/<string(length=2):target>", methods=["POST"]
)
@spec.validate(resp=Response("HTTP_403", HTTP_200=Resp), tags=["model"])
def predict(source, target, query: Query, json: Data):
    """
    predict demo

    demo for `query`, `data`, `resp`
    """
    print(f"=> from {source} to {target}")  # path
    print(f"JSON: {json}")  # Data
    print(f"Query: {query}")  # Query
    if random() < 0.5:
        abort(403)

    return jsonify(label=int(10 * random()), score=random())


@app.route("/api/header", methods=["POST"])
@spec.validate(resp=Response("HTTP_203"), tags=["test", "demo"])
def with_code_header(headers: Header, cookies: Cookie):
    """
    demo for JSON with status code and header
    """
    return jsonify(language=headers.Lang), 203, {"X": 233}


@app.route("/api/file_upload", methods=["POST"])
@spec.validate(resp=Response(HTTP_200=FileResp), tags=["file-upload"])
def with_file(form: File):
    """
    post multipart/form-data demo

    demo for 'form'
    """
    file = form.file
    return {"filename": file.filename, "type": file.content_type}


class UserAPI(MethodView):
    @spec.validate(resp=Response(HTTP_200=Resp), tags=["test"])
    def post(self, json: Data):
        return jsonify(label=int(10 * random()), score=random())


if __name__ == "__main__":
    """
    cmd:
        http :8000/api/user uid=12 limit=1 vip=false
        http ':8000/api/predict/zh/en?text=hello' vip=true uid=aa limit=1
        http POST :8000/api/header Lang:zh-CN Cookie:key=hello
    """
    app.add_url_rule("/api/user", view_func=UserAPI.as_view("user_id"))
    spec.register(app)
    app.run(port=8000)
