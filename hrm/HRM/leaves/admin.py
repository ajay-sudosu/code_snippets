from django.contrib import admin
from .models import *


class LeaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'dept_name', 'status', 'start_date', 'end_date', 'reason','remaining_leaves', 'attachments', 'comments', 'approval_by', 'days')


admin.site.register(Leaves, LeaveAdmin)

class LeavesDetailsAdmin(admin.ModelAdmin):
    list_display = ('leave', 'leave_type', 'status', 'start_date', 'end_date', 'start_time', 'end_time')


admin.site.register(LeavesDetails, LeavesDetailsAdmin)
