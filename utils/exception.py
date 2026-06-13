import logging
import traceback

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)
DEBUG_MODE = True


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'code': exc.status_code, 'message': exc.detail, 'data': None}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_msg = str(exc.orig)
    if 'username_UNIQUE' in error_msg or 'username' in error_msg.lower():
        detail = '用户名已存在'
    elif 'phone_UNIQUE' in error_msg or 'phone' in error_msg.lower():
        detail = '手机号已被注册'
    elif 'email_UNIQUE' in error_msg or 'email' in error_msg.lower():
        detail = '邮箱已被注册'
    elif 'FOREIGN KEY' in error_msg:
        detail = '关联数据不存在'
    elif 'Duplicate entry' in error_msg:
        detail = '用户名已存在'
    else:
        detail = '数据约束冲突，请检查输入'
    return JSONResponse(
        status_code=400,
        content={'code': 400, 'message': detail, 'data': None}
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    print(f"\n========== SQLAlchemy 异常 {request.method} {request.url.path} ==========", flush=True)
    traceback.print_exc()
    print("=" * 60, flush=True)
    return JSONResponse(
        status_code=500,
        content={'code': 500,
                 'message': f'数据库操作失败: {type(exc).__name__}:{exc}' if DEBUG_MODE else '数据库操作失败，请稍后重试',
                 'data': None}
    )


async def general_exception_handler(request: Request, exc: Exception):
    print(f"\n========== 未处理异常 {request.method} {request.url.path} ==========", flush=True)
    traceback.print_exc()
    print("=" * 60, flush=True)
    return JSONResponse(
        status_code=500,
        content={'code': 500,
                 'message': f'服务器内部错误: {type(exc).__name__}: {exc}' if DEBUG_MODE else '服务器内部错误',
                 'data': None}
    )
