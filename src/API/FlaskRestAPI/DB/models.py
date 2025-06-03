import os
import re
import datetime

from flask import request, jsonify

from flask_restful import Resource, reqparse, abort, fields, marshal_with
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flasgger import swag_from
from FlaskRestAPI.app.httpresponses import *

import logging

logger = logging.getLogger(__name__) 

model_file_fields = {
    'name': fields.String,
    'size': fields.Integer,
    'created': fields.String,
    'modified': fields.String
}
model_fields= {
	'ticker': fields.String,
	'models': fields.List(fields.Nested(model_file_fields))
}

class MLModel(Resource):
    @swag_from({
        "tags": ["Models"],
        "summary": "Get price prediction for a specific ticker using a selected model",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "example": "btc"
                        },
                        "model": {
                            "type": "string",
                            "example": "lstm_btc_model1.h5"
                        }
                    },
                    "required": ["ticker", "model"]
                }
            }
        ],
        "responses": {
            200: {
                "description": "Price prediction for the ticker using a selected model",
            },
            400: {
                "description": "Missing ticker or model in request body"
            }
        }
    })
    @marshal_with(model_fields)
    def post(self):
        pass

class MLModels(Resource):

    @swag_from({
        "tags": ["Models"],
        "summary": "Get available ML models for a specific ticker",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "example": "btc"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        ],
        "responses": {
            200: {
                "description": "List of models for the ticker",
                "schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "example": "BTC"
                        },
                        "models": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "example": "lstm_btc_model1.h5"},
                                    "size": {"type": "integer", "example": 2048576},
                                    "created": {"type": "string", "example": "2024-11-01T14:32:17"},
                                    "modified": {"type": "string", "example": "2025-05-28T10:17:45"}
                                }
                            }
                        }
                    }
                }
            },
            204: {'description': 'No data retrieved for given input arguments'},
            400: {
                "description": "Missing ticker in request body"
            }
        }
    })
    @marshal_with(model_fields)
    def post(self):
        try:
            data = request.get_json()
            ticker = data.get("ticker")
            #get only a specified crypto coin if exists
            logger.info(f"GET: Get available models for CryptoCoin with ticker={ticker} request received")
            models = get_model_file_names(ticker)
            if not models:
                logger.info(f"GET: No models found for ticker={ticker}")
                return {'ticker': ticker, 'models': []}, HTTP_NO_CONTENT 
            # Return the list of model names
            return {'ticker': ticker, 'models': models}, HTTP_OK
        except BadRequest as e:
            e_message = f"Internal error: [{str(e)}], operation aborted"
            logger.error(e_message)
            abort(HTTP_BAD_REQUEST, message=e_message)

def get_model_file_names(ticker: str):
    folder = os.getenv("ML_MODELS_PATH","./models")
    pattern = re.compile(rf"^lstm_{re.escape(ticker)}_.*\.h5$")
    if not os.path.exists(folder):
        e_message = f"Folder {folder} does not exist."
        logger.error(e_message)
        abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)
    if not os.path.isdir(folder):
        e_message = f"Path {folder} is not a directory."
        logger.error(e_message)
        abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)
    # List all files in the directory and filter by the pattern
    matching_files = []
    logger.info(f"Searching for model files in {folder} with pattern {pattern.pattern}")
    try:
        for file_name in os.listdir(folder):
            if not pattern.match(file_name):
                continue
            full_path = os.path.join(folder, file_name)
            #skip folders
            if os.path.isdir(full_path):
                continue
            stat = os.stat(full_path)
            matching_files.append({
                "name": file_name,
                "size": stat.st_size,
                "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return matching_files
    except OSError as e:
        e_message = f"Error accessing folder {folder}: {e}"
        logger.error(e_message)
        abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)

'''
import pickle

with open("scaler.pkl", "wb") as f:
    pass
    #pickle.dump(scaler, f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
'''