from django.contrib import admin
from ai.models import AIUsageLog


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('provider_name', 'prompt_tokens', 'completion_tokens',
                    'total_tokens', 'cost_usd', 'created_at', 'receipt', 'receipt_owner',)

