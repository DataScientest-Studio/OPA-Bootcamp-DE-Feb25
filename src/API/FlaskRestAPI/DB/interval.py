from flask import request
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flasgger import swag_from
from werkzeug.exceptions import BadRequest

from FlaskRestAPI.app.definition import db
from FlaskRestAPI.DB.tables import INTERVAL_T
from FlaskRestAPI.app.httpresponses import *

from marshmallow import Schema, ValidationError
from marshmallow import fields as mm_fields

import logging


logger = logging.getLogger(__name__) 

class IntervalSchema(Schema):
    id = mm_fields.Int(dump_only=True)  # Optional; usually assigned by DB
    name_long = mm_fields.String(required=True)
    name_short = mm_fields.String(required=True)

interval_schema = IntervalSchema(many=True)

class IntervalModel(db.Model):
	__tablename__ = INTERVAL_T

	id = db.Column(db.Integer, primary_key=True)
	name_long = db.Column(db.String(30), nullable=False)
	name_short = db.Column(db.String(2), unique=True, nullable=False)

#	candels_cascade = db.relationship('CryptoCoinCandleModel',
#								   backref=INTERVAL_T, cascade="all, delete-orphan")

	def __repr__(self):
		return f"Interval(name_long = {self.name_long}, name_short = {self.name_short})"

interval_args = reqparse.RequestParser()
interval_args.add_argument("name_long", type=str, help="Argumet [name_long] is required", required=True)
interval_args.add_argument("name_short", type=str, help="Argumet [name_short] is required", required=True)

resource_fields_interval= {
	'id': fields.Integer,
	'name_long': fields.String,
	'name_short': fields.String
}

def abort_if_interval_id_doesnt_exist(interval_id):
	if not interval_id:
		e_message = f"Missing required parameter: [interval_id]"
		logger.error(e_message)
		abort(HTTP_BAD_REQUEST, message=e_message)
	interval = db.session.get(IntervalModel,interval_id)
	if not interval:
		e_message = f"Could not find Interval with id={interval_id}, operation aborted"
		logger.error(e_message)
		abort(HTTP_NOT_FOUND , message=e_message)
	return interval

def abort_if_interval_id_taken(interval_id):
	interval = db.session.get(IntervalModel,interval_id)
	if interval:
		e_message = f"Interval id={interval_id} is already taken, operation aborted"
		logger.error(e_message)
		abort(HTTP_CONFLICT , message=e_message)
	return interval

class Intervals(Resource):
	@swag_from({
		'tags': ['Interval'],
		'summary' : 'Lists all available Interval items',
		'responses': {
			200: {
				'description': 'A list of available Interval items',
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
			500: {'description': 'Database error'}
		}
	})
	@marshal_with(resource_fields_interval)
	def get(self):
			try:
				logger.info("GET: Get all intervals request received")
				intervals = IntervalModel.query.all()
				return intervals, HTTP_OK
			except SQLAlchemyError as ex:
				ex_message = f"GET: Database error occurred: [{str(ex)}], operation aborted"
				logger.error(ex_message)
				db.session.rollback()
				abort(HTTP_INTERNAL_SERVER_ERROR, message=ex_message)

	@swag_from({
        'tags': ['Interval'],
		'summary': 'Creates all provided Interval items',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
				'schema': {
					'type': 'array',
					'items': {
						'type': 'object',
						'required': ['name_long', 'name_short'],
						'properties': {
							'name_long': {'type': 'string'},
							'name_short': {'type': 'string'}
						}
					}
				}
            }
        ],
		'responses': {
			201: {
				'description': 'All Intervals created successfully',
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
            400: {'description': 'Data validation error or No input data provided'},
            409: {'description': 'Integrity error: [name_long] or [name_short] NOT unique'},
			500: {'description': 'Database error'}
		}
    })
	@marshal_with(resource_fields_interval)
	def post(self):
		try:
			logger.info("POST: Create intervals request received")
			json_data = request.get_json(force=True, silent=False)
			if not json_data:
				logger.error("POST: No input data provided")
				abort(HTTP_BAD_REQUEST, message="No input data provided")
			validated_intervals = interval_schema.load(request.get_json())
			intervals_added = [IntervalModel(**data) for data in validated_intervals]
			db.session.add_all(intervals_added)
			db.session.commit()
			return intervals_added, HTTP_CREATED 
		except BadRequest as err:
			logger.error(f"POST: BadRequest: Invalid JSON format {err}")
			db.session.rollback()
			abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
		except ValidationError as err:
			logger.error(f"POST: ValidationError: Invalid JSON format {err}")
			db.session.rollback()
			abort(HTTP_BAD_REQUEST, message=f"Invalid JSON format", errors=err.messages)
		except IntegrityError as ex:
			ex_message = f"POST: Integrity error occurred: [{ex.orig}], operation aborted"
			logger.error(ex_message)
			db.session.rollback()
			abort(HTTP_CONFLICT , message=ex_message)
		except SQLAlchemyError as ex:
			ex_message = f"POST: Database error occurred: [{str(ex)}], operation aborted"
			logger.error(ex_message)
			db.session.rollback()
			abort(HTTP_INTERNAL_SERVER_ERROR, message=ex_message)
		

	@swag_from({
        'tags': ['Interval'],
        'summary': 'Deletes all Interval items from database',
        'responses': {
            200: {'description': 'All interval items deleted'},
            500: {'description': 'Internal Server Error'}
        }
    })
	def delete(self):
		try:
			logger.info("DELETE: Delete all intervals request received")
			db.session.query(IntervalModel).delete()
			db.session.commit()
			return "All interval items deleted", HTTP_OK 
		except SQLAlchemyError as ex:
			ex_message = f"DELETE: Database error occurred: [{str(ex)}], operation aborted"
			logger.error(ex_message)
			db.session.rollback()
			abort(HTTP_INTERNAL_SERVER_ERROR , message=ex_message)

class Interval(Resource):

	@swag_from({
		'tags': ['Interval'],
		'summary': 'Returns the Interval item with the requested ID',
		'parameters': [
			{
				'name': 'interval_id',
				'in': 'path',
				'type': 'integer',
				'required': True,
				'description': 'ID of the Interval item to get'
			}
		],
		'responses': {
			200: {
				'description': 'A single interval item',
				'schema': {
					'type': 'object',
					'properties': {
						'id': {'type': 'integer'},
						'name_long': {'type': 'string'},
						'name_short': {'type': 'string'}
					}
				}
			},
			404: {'description': 'Item NOT found'},
			500: {'description': 'Database error'}
		}
	})
	@marshal_with(resource_fields_interval)
	def get(self, interval_id):
		try:
			logger.info(f"GET: Get interval with id={interval_id} request received")
			interval = abort_if_interval_id_doesnt_exist(interval_id)
			return interval, HTTP_OK
		except SQLAlchemyError as ex:
			ex_message = f"GET: Database error occurred: [{str(ex)}], operation aborted"
			logger.error(ex_message)
			abort(HTTP_INTERNAL_SERVER_ERROR, message=ex_message)

	@swag_from({
		'tags': ['Interval'],
		'summary': 'Updates an Interval item, specified by requested ID',
		'parameters': [
			{
				'name': 'interval_id',
				'in': 'path',
				'type': 'integer',
				'required': True,
				'description': 'Interval ID to update'
			},
			{
				'name': 'body',
				'in': 'body',
				'required': True,
				'schema': {
					'type': 'object',
					'required': ['name_long', 'name_short'],
					'properties': {
						'name_long': {'type': 'string'},
						'name_short': {'type': 'string'}
					}
				}
			}
		],
		'responses': {
			200: {
				'description': 'Interval updated successfully',
				'schema': {
					'type': 'object',
					'required': ['id', 'name_long', 'name_short'],
					'properties': {
						'id': {'type': 'integer'},
						'name_long': {'type': 'string'},
						'name_short': {'type': 'string'}
					}
				}
			},
			400: {'description': 'Invalid JSON format or No input data provided'},
			404: {'description': 'Item NOT found'},
            409: {'description': 'Integrity error: [name_long] or [name_short] NOT unique'},
			500: {'description': 'Database error'}
		}
	})
	@marshal_with(resource_fields_interval)
	def patch(self, interval_id):
		try:
			logger.info(f"PATCH: Update interval with id={interval_id} request received")
			# Check if the interval ID exists
			json_data = request.get_json(force=True, silent=False)
			if not json_data:
				logger.error("PATCH: No input data provided")
				abort(HTTP_BAD_REQUEST, message="No input data provided")
			interval = abort_if_interval_id_doesnt_exist(interval_id)
			args = interval_args.parse_args()
			interval.name_long = args['name_long']
			interval.name_short = args['name_short']
			db.session.commit()
			return interval, HTTP_OK
		except BadRequest as err:
			logger.error(f"PATCH: BadRequest: Invalid JSON format {err}")
			db.session.rollback()
			abort(HTTP_BAD_REQUEST, message="Invalid JSON format", errors=err.description)		
		except IntegrityError as ex:
			ex_message = f"PATCH: Integrity error occurred: [{ex.orig}], operation aborted"
			logger.error(ex_message)
			db.session.rollback()
			abort(HTTP_CONFLICT , message=e_message)
		except SQLAlchemyError as ex:
			ex_message = f"PATCH: Database error occurred: [{str(ex)}], operation aborted"
			logger.error(ex_message)
			db.session.rollback()
			abort(HTTP_INTERNAL_SERVER_ERROR, message=ex_message)
		
	@swag_from({
		'tags': ['Interval'],
		'summary': 'Deletes an Interval item with the requested ID',
		'parameters': [
			{
				'name': 'interval_id',
				'in': 'path',
				'type': 'integer',
				'required': True,
				'description': 'Interval ID to delete'
			}
		],
		'responses': {
			200: {'description': 'Interval deleted successfully'},
			404: {'description': 'Item NOT found'},
			500: {'description': 'Database error'}
		}
	})	
	def delete(self, interval_id):
		try:
			logger.info(f"DELETE: Delete interval with id={interval_id} request received")
			# Check if the interval ID exists
			interval = abort_if_interval_id_doesnt_exist(interval_id)
			db.session.delete(interval)
			db.session.commit()
			return f"Interval id={interval_id} deleted", HTTP_OK 
		except SQLAlchemyError as ex:
			ex_message = f"DELETE: Database error occurred: [{str(ex)}], operation aborted"
			logger.error(e_message)
			db.session.rollback()
			abort(HTTP_INTERNAL_SERVER_ERROR , message=ex_message)
