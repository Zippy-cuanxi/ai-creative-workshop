"""SPA 兜底：单容器部署时，非 /api、非 /admin 路由都交给前端 index.html。"""
from django.conf import settings
from django.http import FileResponse, JsonResponse


def spa_index(request):
    index_file = settings.FRONTEND_DIST / "index.html"
    if index_file.exists():
        response = FileResponse(open(index_file, "rb"), content_type="text/html; charset=utf-8")
        response["Cache-Control"] = "no-cache"
        return response
    return JsonResponse({
        "ok": True,
        "service": "ai-creative-workshop",
        "message": "后端已启动，但未检测到前端构建产物（FRONTEND_DIST）。",
        "api": ["/api/models", "/api/generate", "/api/usage", "/api/templates", "/api/health"],
    })
