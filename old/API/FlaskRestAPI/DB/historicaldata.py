from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
#from sqlalchemy import func
from datetime import datetime
from flasgger import swag_from
from werkzeug.exceptions import BadRequest

from FlaskRestAPI.app.definition import db
from FlaskRestAPI.DB.tables import HISTORICAL_DATA_T
from FlaskRestAPI.app.httpresponses import *


class HistoricalDataModel(db.Model):
    __tablename__ = HISTORICAL_DATA_T

    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"HistoricalData(updated_at = {self.updated_at}"

historical_data_put_args = reqparse.RequestParser()
historical_data_put_args.add_argument("updated_at", type=str, help="Argument [updated_at] is required", required=True)

resource_fields_historical_data = {
	'id': fields.Integer,
    'updated_at': fields.DateTime
    }

class HistoricalData(Resource):

    @swag_from({
    'tags': ['Historical Data'],
    'summary': 'Create a new historical data entry',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Historical data to create',
            'schema': {
                'type': 'object',
                'required': ['updated_at'],
                'properties': {
                    'updated_at': {'type': 'string', 'example': '2022-01-01T12:00:00.789123+00:00', 'description': 'in ISO 8601 format'},
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Historical data created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'updated_at': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Invalid JSON format or No input data provided'},
        500: {'description': 'Internal server error'}
    }
    })
    @marshal_with(resource_fields_historical_data)
    def post(self):
        try:
            json_data = request.get_json(force=True, silent=False)
            if not json_data:
                abort(HTTP_BAD_REQUEST, message="No input data provided")
            args = historical_data_put_args.parse_args()
#            max_id = db.session.query(func.max(HistoricalDataModel.id)).scalar()
#            next_id = (max_id or 0) + 1
            historical_data = HistoricalDataModel(updated_at=datetime.fromisoformat(args['updated_at']))
            db.session.add(historical_data)
            db.session.commit()
            return historical_data, HTTP_CREATED 
        except ValueError as err:
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message=f"Invalid date format {err}")		
        except BadRequest as err:
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
        except SQLAlchemyError as ex:
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR, message=f"Database error occurred: [{str(ex)}], operation aborted")

    @swag_from({
        'tags': ['Historical Data'],
        'summary': 'Retrieve all historical data entries',
        'responses': {
            200: {
                'description': 'A list of all historical data entries',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'updated_at': {'type': 'string'}
                        }
                    }
                }
            },
            204: {'description': 'No data retrieved for given input arguments'},
            500: {'description': 'Internal server error'}
        }
    })
    @marshal_with(resource_fields_historical_data)
    def get(self):
        try:
            historical_data = HistoricalDataModel.query.all()
            return historical_data, HTTP_OK if len(historical_data) > 0 else HTTP_NO_CONTENT
        except SQLAlchemyError as ex:
            abort(HTTP_INTERNAL_SERVER_ERROR, message=f"Database error occurred: [{str(ex)}], operation aborted")
            
