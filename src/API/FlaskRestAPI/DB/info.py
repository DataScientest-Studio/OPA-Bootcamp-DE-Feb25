from flasgger import swag_from
from flask_restful import Resource

from FlaskRestAPI.app.definition import app_version
from FlaskRestAPI.app.httpresponses import HTTP_OK

import logging


logger = logging.getLogger(__name__) 

class Info(Resource):
	@swag_from({
		'tags': ['Info'],
		'summary' : 'Application information',
		'responses': {
			200: {
				'schema': {
					'type': 'object',
					'required': ['info', 'ApiDoc'],
					'properties': {
						'info': {'type': 'string'},
						'ApiDoc': {'type': 'string'}
					}
				}
			}
		}
	})
	def get(self):
		logger.info("GET: Get info request received")
		return {'info':f"DataScientest: OPE project, Version {app_version}",
				'ApiDoc': f'Call [http://host:port/apispec_1.json] to get the API specification in JSON format'}, HTTP_OK