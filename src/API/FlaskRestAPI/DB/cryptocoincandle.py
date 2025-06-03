from flask import request
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from sqlalchemy import and_, literal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import re
from flasgger import swag_from
from werkzeug.exceptions import BadRequest

from marshmallow import Schema, ValidationError
from marshmallow import fields as mm_fields

from FlaskRestAPI.app.definition import db
from FlaskRestAPI.DB.tables import CRYPTO_COIN_T, INTERVAL_T, CRYPTO_COIN_CANDLE_T
from FlaskRestAPI.app.httpresponses import *
from FlaskRestAPI.DB.cryptocoin import CryptoCoinModel
from FlaskRestAPI.DB.interval import IntervalModel

import logging


logger = logging.getLogger(__name__) 

class CryptoCoinCandleSchema(Schema):
    #id = mm_fields.Int(dump_only=True)  # Optional; usually assigned by DB
    crypto_id = mm_fields.Int(required=True)
    interval_id = mm_fields.Int(required=True)
    open_price = mm_fields.Float(required=True)
    close_price = mm_fields.Float(required=True)
    high_price = mm_fields.Float(required=True)
    low_price = mm_fields.Float(required=True)
    volume = mm_fields.Float(required=True)
    open_time = mm_fields.DateTime(required=True, format='iso')
    close_time = mm_fields.DateTime(required=True, format='iso')

ccc_schema = CryptoCoinCandleSchema(many=True)

class CryptoCoinCandleModel(db.Model):
    __tablename__ = CRYPTO_COIN_CANDLE_T

    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.Integer, db.ForeignKey(CRYPTO_COIN_T + '.id'), nullable=False)
    interval_id = db.Column(db.Integer, db.ForeignKey(INTERVAL_T + '.id'), nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    open_time = db.Column(db.DateTime, nullable=False)
    close_time = db.Column(db.DateTime, nullable=False)
	
    def __repr__(self):
        return f"CryptoCoinCandle(id = {self.id}, crypto_id = {self.crypto_id}, interval_id = {self.interval_id})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'crypto_id': self.crypto_id,
            'interval_id': self.interval_id,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'volume': self.volume,
            'open_time': self.open_time.isoformat() if self.open_time else None,
            'close_time': self.close_time.isoformat() if self.close_time else None
        }
    
cc_candle_get_args = reqparse.RequestParser()
cc_candle_get_args.add_argument("ticker", type=str, location='args', help="Argumet [ticker] is required", required=True)
cc_candle_get_args.add_argument("startDate", type=str, location='args', help="Argumet [startDate] is required and must be in format YYYYMMDDhhmmss", required=True)
cc_candle_get_args.add_argument("endDate", type=str, location='args', help="Argumet [endDate] is required and must be in format YYYYMMDDhhmmss", required=False)
cc_candle_get_args.add_argument("interval", type=str, location='args', help="Argumet [interval] is required", required=True)

cc_candle_post_args = reqparse.RequestParser()
cc_candle_post_args.add_argument("crypto_id", type=int, help="Argumet [crypto_id] is required", required=True)
cc_candle_post_args.add_argument("interval_id", type=int, help="Argumet [interval_id] is required", required=True)
cc_candle_post_args.add_argument("open_price", type=float, help="Argumet [open_price] is required", required=True)
cc_candle_post_args.add_argument("close_price", type=float, help="Argumet [close_price] is required", required=True)
cc_candle_post_args.add_argument("high_price", type=float, help="Argumet [high_price] is required", required=True)
cc_candle_post_args.add_argument("low_price", type=float, help="Argumet [low_price] is required", required=True)
cc_candle_post_args.add_argument("volume", type=float, help="Argumet [volume] is required", required=True)
cc_candle_post_args.add_argument("close_time", type=str, help="Argumet [close_time] is required", required=True)

resource_fields_crypto_coin_candle= {
	'id': fields.Integer,
	'crypto_id': fields.Integer,
	'interval_id': fields.Integer,
    'open_price': fields.Float,
    'close_price': fields.Float,
    'high_price': fields.Float,
    'low_price': fields.Float,
    'volume': fields.Float,
    'open_time': fields.DateTime,
    'close_time': fields.DateTime
}

resource_fields_crypto_coin= {
    'open_price': fields.Float,
    'close_price': fields.Float,
    'high_price': fields.Float,
    'low_price': fields.Float,
    'volume': fields.Float,
    'open_time': fields.DateTime,
    'close_time': fields.DateTime,
    'ticker': fields.String,
    'interval': fields.String
}

def abort_if_invalid_date_format(arg_name: str, timestamp_str: str) -> datetime:
    '''
    Validates and parses a timestamp string to a datetime object.
    
    :param arg_name: The datetime argument: startDate or endDate.
    :param timestamp_str: The datetime format to expect. The expected format is: '%Y%m%d%H%M%S'.
    :return: A datetime object if valid, otherwise aborts a HTTP request with HTTP_BAD_REQUEST error.
    '''
    format = "%Y%m%d%H%M%S"
    date_pattern = r"^\d{4}\d{2}\d{2}\d{2}\d{2}\d{2}"
    if not re.match(date_pattern, timestamp_str):
        e_message = f"Argumnet [{arg_name}] error: invalid date format. Valid format : YYYYMMDDhhmmss."
        logger.error(e_message)
        abort(HTTP_BAD_REQUEST, message=e_message)
    try:
       return datetime.strptime(timestamp_str, format)
    except ValueError:
        e_message = f"Argumnet [{arg_name}] error: invalid date format. Valid format : YYYYMMDDhhmmss."
        logger.error(e_message)
        abort(HTTP_BAD_REQUEST, message=e_message)


def abort_if_invalid_args(args):
    ticker_arg_val = args['ticker']
    startDate_arg_val = args['startDate']
    endDate_arg_val = args['endDate']
    interval_arg_val = args['interval']

    ticker_db = CryptoCoinModel.query.filter_by(ticker=ticker_arg_val).first()
    if not ticker_db:
        e_message = f"Argumnet [ticker] error: [{ticker_arg_val}] does not exist."
        logger.error(e_message)
        abort(HTTP_NOT_FOUND, message=e_message)

    startDateTime = abort_if_invalid_date_format(arg_name='startDate', timestamp_str=startDate_arg_val)
    if endDate_arg_val:
        endDateTime = abort_if_invalid_date_format(arg_name='endDate', timestamp_str=endDate_arg_val)
    else:
        endDateTime = None

    interval_db = IntervalModel.query.filter_by(name_short=interval_arg_val).first()
    if not interval_db:
        e_message = f"Argumnet [interval] error: [{interval_arg_val}] is not supported."
        logger.error(e_message)
        abort(HTTP_NOT_FOUND, message=e_message)
    
    return ticker_db.id, startDateTime, endDateTime, interval_db.id

def abort_if_record_invalid(record):
    pass

class CryptoCoinCandle(Resource):
    
    @swag_from({
        'tags': ['Crypto Coin candle'],
        'summary': 'Get Crypto Coin Candle data based on the provided query arguments',
        'parameters': [
            {
                'name': 'ticker',
                'in': 'query',
                'type': 'string',
                'required': True,
                'description': 'The ticker of the Crypto Coin to filter by'
            },
            {
                'name': 'startDate',
                'in': 'query',
                'type': 'string',
                'required': True,
                'description': 'The start date for the filter (ISO 8601 format)'
            },
            {
                'name': 'endDate',
                'in': 'query',
                'type': 'string',
                'required': False,
                'description': 'The end date for the filter (ISO 8601 format)'
            },
            {
                'name': 'interval',
                'in': 'query',
                'type': 'string',
                'required': True,
                'description': 'The Interval''s short name for the filter'
            }
        ],
        'responses': {
            200: {
                'description': 'A list of CryptoCoinCandles',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'open_price': {'type': 'number'},
                            'close_price': {'type': 'number'},
                            'high_price': {'type': 'number'},
                            'low_price': {'type': 'number'},
                            'volume': {'type': 'number'},
                            'open_time': {'type': 'string'},
                            'close_time': {'type': 'string'},
                            'ticker': {'type': 'string'},
                            'interval': {'type': 'string'}
                        }
                    }
                }
            },
            204: {'description': 'No data retrieved for given input arguments'},
            404: {'description': 'Invalid input arguments'},
            500: {'description': 'Internal server error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def get(self):
        try:
            logger.info("GET: CryptoCoinCandle GET request received")
            args = cc_candle_get_args.parse_args()
            ticker_id, startDate, endDate, interval_id = abort_if_invalid_args(args)
            if not endDate: 
                candles = CryptoCoinCandleModel.query.filter(
                                        and_(
                                            CryptoCoinCandleModel.crypto_id == ticker_id, 
                                            CryptoCoinCandleModel.interval_id == interval_id,
                                            CryptoCoinCandleModel.close_time >= startDate)
                                        ).with_entities(
                                            CryptoCoinCandleModel.open_price,
                                            CryptoCoinCandleModel.close_price,
                                            CryptoCoinCandleModel.high_price,
                                            CryptoCoinCandleModel.low_price,
                                            CryptoCoinCandleModel.volume,
                                            CryptoCoinCandleModel.open_time,
                                            CryptoCoinCandleModel.close_time,
                                            literal(args['ticker']).label("ticker"),
                                            literal(args['interval']).label("interval")                                        
                                        ).all()
            else:
                candles = CryptoCoinCandleModel.query.filter(
                                        and_(
                                            CryptoCoinCandleModel.crypto_id == ticker_id, 
                                            CryptoCoinCandleModel.interval_id == interval_id,
                                            CryptoCoinCandleModel.close_time.between(startDate,endDate))
                                        ).with_entities(
                                            CryptoCoinCandleModel.open_price,
                                            CryptoCoinCandleModel.close_price,
                                            CryptoCoinCandleModel.high_price,
                                            CryptoCoinCandleModel.low_price,
                                            CryptoCoinCandleModel.volume,
                                            CryptoCoinCandleModel.open_time,
                                            CryptoCoinCandleModel.close_time,                                     
                                            literal(args['ticker']).label("ticker"),
                                            literal(args['interval']).label("interval")                                        
                                        ).all()

            #.query(CryptoCoinModel, CryptoCoinCandleModel, IntervalModel)\
            #.join(CryptoCoinModel, CryptoCoinCandleModel, IntervalModel)\
            #.join(CryptoCoinCandleModel, CryptoCoinModel.id == CryptoCoinCandleModel.crypto_id)\
            #.join(IntervalModel, CryptoCoinCandleModel.interval_id == IntervalModel.id)\
            #.all()
                        
            return candles, HTTP_OK if len(candles) > 0 else HTTP_NO_CONTENT
        except BadRequest as err:
            e_message = f"Invalid JSON format: {err.description}"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
        except SQLAlchemyError as ex:
            e_message = f"Database error occurred: [{str(ex)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)
    
    @swag_from({
        'tags': ['Crypto Coin candle'],
        'summary': 'Add new Crypto Coin candle records',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'crypto_id': {'type': 'integer'},
                            'interval_id': {'type': 'integer'},
                            'open_price': {'type': 'number'},
                            'close_price': {'type': 'number'},
                            'high_price': {'type': 'number'},
                            'low_price': {'type': 'number'},
                            'volume': {'type': 'number'},
                            'open_time': {'type': 'string'},
                            'close_time': {'type': 'string'}
                        }
                    }
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Records successfully added',
                'schema': {
                    'type': 'string',
                    'example': 'n=2 record(s) successfully added'
                }
            },
            400: {'description': 'Invalid JSON format or No input data provided'},
            409: {'description': 'Conflict error, data already exists'},
            500: {'description': 'Internal server error'}
        }
    })
    def post(self):
        try:
            logger.info("POST: CryptoCoinCandle POST request received")
            json_data = request.get_json(force=True, silent=False)
            if not json_data:
                logger.error("POST: No input data provided")
                db.session.rollback()
                abort(HTTP_BAD_REQUEST, message="No input data provided")
            validated_candels = ccc_schema.load(json_data)
            db.session.bulk_save_objects([CryptoCoinCandleModel(**data) for data in validated_candels])
            db.session.commit()    
            return f"n={len(json_data)} record(s) successfully added", HTTP_CREATED 
        except BadRequest as err:
            e_message = f"Invalid JSON format: BadRequest : {err.description}"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
        except ValidationError as err:
            e_message = f"Invalid JSON format: ValidationError : {err.messages}"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message=f"Invalid JSON format", errors=err.messages)
        except IntegrityError as ex:
            e_message = f"Integrity error occurred: [{ex.orig}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_CONFLICT , message=f"Integrity error occurred: [{ex.orig}], operation aborted")
        except SQLAlchemyError as ex:
            e_message = f"Database error occurred: [{str(ex)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR, message=f"Database error occurred: [{str(ex)}], operation aborted")
        