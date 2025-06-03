from flask import request

from flask_restful import Resource, reqparse, abort, fields, marshal_with
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flasgger import swag_from
from werkzeug.exceptions import BadRequest

from FlaskRestAPI.app.definition import db
from FlaskRestAPI.DB.tables import CRYPTO_COIN_T
from FlaskRestAPI.app.httpresponses import *

from marshmallow import Schema, ValidationError
from marshmallow import fields as mm_fields

import logging


logger = logging.getLogger(__name__) 

class CryptoCoinSchema(Schema):
    id = mm_fields.Int(dump_only=True)  # Optional; usually assigned by DB
    name = mm_fields.String(required=True)
    ticker = mm_fields.String(required=True)

cc_schema = CryptoCoinSchema(many=True)

class CryptoCoinModel(db.Model):
    __tablename__ = CRYPTO_COIN_T
        
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    ticker = db.Column(db.String(7), unique=True, nullable=False)

#    candels_cascade = db.relationship('FlaskRestAPI.DB.cryptocoincandle.CryptoCoinCandleModel', 
#									  backref=CRYPTO_COIN_T, cascade="all, delete-orphan")

    def __repr__(self):
        return f"CryptoCoin(name = {self.name}, ticker = {self.ticker})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ticker': self.ticker
        }
    
crypto_coin_args = reqparse.RequestParser()
crypto_coin_args.add_argument("name", type=str, help="Argument [name] is required", required=True)
crypto_coin_args.add_argument("ticker", type=str, help="Argument [ticker] is required", required=True)

crypto_coin_del_args = reqparse.RequestParser()
crypto_coin_del_args.add_argument("crypto_id", type=int, help="Argument [crypto_id] is required", required=True)

resource_fields_crypto_coin= {
	'id': fields.Integer,
	'name': fields.String,
	'ticker': fields.String
}

def abort_if_crypto_id_doesnt_exist(crypto_id: int) -> CryptoCoinModel:
    if not crypto_id:
        logger.error("Missing required parameter: [crypto_id]")
        abort(HTTP_BAD_REQUEST, message=f"Missing required parameter: [crypto_id]")
    crypto_coin = db.session.get(CryptoCoinModel, crypto_id)
    if not crypto_coin:
        e_message = f"Could not find CryptoCoin with id={crypto_id}, operation aborted"
        logger.error(e_message)
        abort(HTTP_NOT_FOUND , message=e_message)
    return crypto_coin

def abort_if_crypto_id_taken(crypto_id: int) -> CryptoCoinModel:
    crypto_coin = CryptoCoinModel.query.filter_by(id=crypto_id).first()
    if crypto_coin:
        e_message = f"CryptoCoin id={crypto_id} is already taken, operation aborted"
        logger.error(e_message)
        abort(HTTP_NOT_ACCEPTABLE , message=e_message)
    return crypto_coin

class CryptoCoin(Resource):

    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Get a specific CryptoCoin',
        'parameters': [
            {
                'name': 'crypto_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the crypto coin to retrieve'
            }
        ],
        'responses': {
            200: {
                'description': 'Crypto Coin found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'ticker': {'type': 'string'}
                    }
                }
            },
            404: {'description': 'Crypto Coin not found'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def get(self, crypto_id):
        try:
            #get only a specified crypto coin if exists
            logger.info(f"GET: Get CryptoCoin with id={crypto_id} request received")
            crypto_coin = abort_if_crypto_id_doesnt_exist(crypto_id)
            return crypto_coin, HTTP_OK
        except SQLAlchemyError as e:
            e_message = f"Database error occurred: [{str(e)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)
    
    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Update an existing Crypto Coin',
        'parameters': [
            {
                'name': 'crypto_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the Crypto Coin to update'
            },
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'ticker': {'type': 'string'}
                    }
                }
            }
        ],
        'responses': {
            200: {'description': 'Crypto Coin updated'},
            400: {'description': 'Invalid JSON format or No input data provided'},
            404: {'description': 'Crypto Coin not found'},
            409: {'description': 'Integrity error: [name] or [ticker] NOT unique'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def patch(self, crypto_id):
        try:
            logger.info(f"PATCH: Update CryptoCoin with id={crypto_id} request received")
            #update only a specified crypto coin if exists
            json_data = request.get_json(force=True, silent=False)
            if not json_data:
                logger.error("PATCH: No input data provided")
                db.session.rollback()
                abort(HTTP_BAD_REQUEST, message="No input data provided")
            crypto_coin = abort_if_crypto_id_doesnt_exist(crypto_id)
            args = crypto_coin_args.parse_args()
            crypto_coin.name = args['name']
            crypto_coin.ticker = args['ticker']
            db.session.commit()
            return crypto_coin, HTTP_OK
        except BadRequest as err:
            e_message = f"Invalid JSON format: [{err.description}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
        except IntegrityError as e:
            e_message = f"Integrity error occurred: [{e.orig}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_CONFLICT , message=e_message)
        except SQLAlchemyError as e:
            e_message = f"Database error occurred: [{str(e)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR , message=e_message)
        
    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Delete a Crypto Coin',
        'parameters': [
            {
                'name': 'crypto_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the Crypto Coin to delete'
            }
        ],
        'responses': {
            200: {'description': 'Crypto Coin deleted'},
            404: {'description': 'Crypto Coin not found'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def delete(self, crypto_id):
        try:
            logger.info(f"DELETE: Delete CryptoCoin with id={crypto_id} request received")
            #delete only a specified crypto coin if exists
            crypto_coin = abort_if_crypto_id_doesnt_exist(crypto_id)
            db.session.delete(crypto_coin)
            db.session.commit()
            return f"CryptoCoin id={crypto_id} deleted", HTTP_OK 
        except SQLAlchemyError as e:
            e_message = f"Database error occurred: [{str(e)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR , message=e_message)

class CryptoCoins(Resource):

    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Get all Crypto Coin records',
        'description': 'Returns a list of all available Crypto Coin records.',
        'responses': {
            200: {
                'description': 'A list of crypto coins',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'ticker': {'type': 'string'}
                        }
                    }
                }
            },
            204: {'description': 'No data retrieved'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def get(self):
        try:
            logger.info(f"GET: Get all CryptoCoin items request received")
            #get all available crypto coins
            crypto_coins = CryptoCoinModel.query.all()
            return crypto_coins, HTTP_OK if len(crypto_coins) > 0 else HTTP_NO_CONTENT
        except SQLAlchemyError as e:
            e_message = f"Database error occurred: [{str(e)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR , message=e_message)

    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Add new Crypto Coin items',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['name', 'ticker'],
                        'properties': {
                            'id': {
                                 'type': 'integer',
                                 'description': 'Optional: ID of thr crypto coin'
                            },
                            'name': {
                                 'type': 'string',
                                 'description': 'Name of the crypto coin'
                            },
                            'ticker': {
                                 'type': 'string',
                                 'description': 'Ticker symbol of the crypto coin'
                            }
                        }
                    }
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Crypto Coin items created successfully',
                'schema': {
					'type': 'array',
					'items': {
						'type': 'object',
						'required': ['id', 'name_long', 'name_short'],
						'properties': {
							'id': {'type': 'integer'},
							'name_long': {'type': 'string'},
							'name_short': {'type': 'string'}
						}
					}
				}
            },
            400: {'description': 'Invalid JSON format or No input data provided'},
            409: {'description': 'Integrity error: [name] or [ticker] NOT unique'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def post(self):
        try:
            logger.info(f"POST: Add new CryptoCoin items request received")
            #add new crypto coins
            json_data = request.get_json(force=True, silent=False)
            if not json_data:
                loader.error("POST: No input data provided")
                db.session.rollback()
                abort(HTTP_BAD_REQUEST, message="No input data provided")
            validated_coins = cc_schema.load(json_data)
            coins_added = [CryptoCoinModel(**data) for data in validated_coins]
            db.session.add_all(coins_added)
            db.session.commit()    
            return coins_added, HTTP_CREATED 
        except BadRequest as err:
            e_message = f"Invalid JSON format: [{err.description}], operation aborted"
            logger.error(e_message) 
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
        except ValidationError as err:
            e_message = f"Validation error: [{err.messages}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_BAD_REQUEST, message=f"Validation failed", errors=err.messages)
        except IntegrityError as ex:
            e_message = f"Integrity error occurred: [{ex.orig}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_CONFLICT , message=e_message)
        except SQLAlchemyError as ex:
            e_message = f"Database error occurred: [{str(ex)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR, message=e_message)

    @swag_from({
        'tags': ['Crypto Coin'],
        'summary': 'Delete all Crypto Coin records',
        'description': 'Deletes all Crypto Coin records from the database',
        'responses': {
            200: {'description': 'All CryptoCoin items deleted'},
            500: {'description': 'Database error'}
        }
    })
    @marshal_with(resource_fields_crypto_coin)
    def delete(self):
        try:
            logger.info(f"DELETE: Delete all CryptoCoin items request received")
            #delete all crypto coins
            db.session.query(CryptoCoinModel).delete()
            db.session.commit()
            return "All CryptoCoin items deleted", HTTP_OK 
        except SQLAlchemyError as e:
            e_message = f"Database error occurred: [{str(e)}], operation aborted"
            logger.error(e_message)
            db.session.rollback()
            abort(HTTP_INTERNAL_SERVER_ERROR , message=e_message)
