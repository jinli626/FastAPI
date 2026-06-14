import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from starlette import status as http_status

from models.admin import Admin
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin/upload", tags=["admin-upload"])

# 上传目录：<backend 根目录>/static/uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的图片类型与对应扩展名
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    _admin: Admin = Depends(get_current_admin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="仅支持 jpg / png / gif / webp 格式的图片"
        )

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过 5MB"
        )

    ext = ALLOWED_TYPES[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 返回绝对 URL，移动端 / 管理端均可直接使用
    url = f"{str(request.base_url).rstrip('/')}/static/uploads/{filename}"
    return success_response(message="上传成功", data={"url": url})
