from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from tortoise.contrib.fastapi import register_tortoise

from core import core_router
from oidc_exceptions import OIDCError
from registration import reg_router
from registration.reg_exceptions import RegistrationError
from settings import _api_settings
from tortoise_config import CONFIG
from utils.redis_client import register_redis, _redis

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=_api_settings.origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
        allow_headers=["*"]
)
app.include_router(core_router)
app.include_router(reg_router)
register_tortoise(app, CONFIG)
register_redis(app, _redis)


# @app.exception_handler(RequestValidationError)
# async def process_pydantic_exceptions(request: Request, exc: RequestValidationError):
#     for error in exc.errors():
#         print(error['type'], error['loc'], error['input'])
#         if error['type'] and error['loc'] == ('query', 'response_type') and error['input'] != 'code':
#             raise UnsupportedResponseTypeError
#     return JSONResponse(status_code=422,
#                         content={'detail': 'custom message', "errors": exc.errors()})
#
#
@app.exception_handler(OIDCError)
async def process_oidc_exceptions(request: Request, exc: OIDCError):
    params = {
        'error': exc.error,
        'error_description': exc.error_description,
        'state': exc.state
    }
    if issubclass(type(exc), RegistrationError):
        exc: RegistrationError
        return JSONResponse(status_code=400,
                            content=params)
    query_str = '&'.join(f'{k}={v}' for k, v in params.items())
    return RedirectResponse(status_code=302,
                            url=f'{exc.redirect_uri}/?{query_str}')


@app.head('/health')
async def healthcheck():
    return
