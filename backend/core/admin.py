from django.contrib import admin

from .models import GenerationLog


@admin.register(GenerationLog)
class GenerationLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tool", "model", "status", "error_code",
                    "latency_ms", "anonymous_id", "request_id")
    list_filter = ("tool", "status", "model")
    search_fields = ("request_id", "anonymous_id", "ip_hash")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
