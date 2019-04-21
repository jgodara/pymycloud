from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest, Unauthorized

from database.models import Users
from database.session import SessionFactoryPool


class ResourceBase(Resource):

    def get_principal(self):
        _db = SessionFactoryPool.get_current_session()
        access_key = self._assert_access_key()
        user = _db.query(Users).filter(
            Users.access_key == access_key).first()
        if not user:
            raise Unauthorized(f"No binding found for {access_key}")

        return user

    def _assert_access_key(self):
        access_key = request.form['access_key']

        if not access_key:
            raise BadRequest("Access key is expected")

        return access_key