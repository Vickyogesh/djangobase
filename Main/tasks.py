from __future__ import absolute_import, unicode_literals
from celery.decorators import task
import random
import requests
import json


def getUPC(asin):
	link = f"https://amzscout.net/calculator/v1/products/COM/{asin}"
	try:
		result = requests.get(link).text
		json_res = json.loads(result)
		return {"Status": "Success"
			,"upc":    json_res['upc']
			,"width":  json_res['size']['width']
			,"height": json_res['size']['height']
			,"depth":  json_res['size']['depth']
			,"weight": json_res['weight']}
	except:
		return {"Status": "Failure"}

def test_oms_credentials(*args, **kwargs):
	"""
		Test not yet built... For now just display a success
	"""
	return {'status':'success'}