from functools import wraps
from flask import session, jsonify,g
from flask import abort

# def login_required(func):
#     @wraps(func)
#     def inner(*args, **kwargs):
#         if g.user:
#             return func(*args, **kwargs)
#         else:
#
#             abort(401)
#             return jsonify(msg='请先登录', isSuccess=False),401
#     return inner