from django.db import models
from user_management.models import Department,CustomUser
from user_management.base import BaseModel

# Create your models here.


class Leaves(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    dept_name = models.ForeignKey(Department, on_delete=models.DO_NOTHING)

    STATUS_CHOICE = (
        ("Accepted", "Accepted"), ("Pending", "Pending"), ("Cancelled", "Cancelled"), ("Partiall Accepted", "Partially Accepted")
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="Pending")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    # start_time = models.TimeField(blank=True, null=True, default=None)
    # end_time = models.TimeField(blank=True, null=True, default=None)
    reason = models.CharField(max_length=200)
    remaining_leaves = models.FloatField()
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)
    comments = models.CharField(max_length=200, null=True, blank=True)
    days = models.FloatField()
    approval_by = models.CharField(max_length=200, null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)


class LeavesDetails(BaseModel):
    leave = models.ForeignKey(Leaves, on_delete=models.DO_NOTHING)
    TYPE_CHOICE = (
        ("Fullday", "Fullday"), ("Halfday", "Halfday"), ("Shortleave", "Shortleave")
    )
    leave_type = models.CharField(max_length=10, choices=TYPE_CHOICE, default="Fullday")
    STATUS_CHOICE = (
        ("Accepted", "Accepted"), ("Pending", "Pending"), ("Cancelled", "Cancelled", "PARTIALLY APPROVED", "PARTIALLY APPROVED")
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICE, default="PENDING")
    start_date = models.DateField(auto_now=False, null=True, blank=True)
    end_date = models.DateField(auto_now=False, null=True, blank=True)
    start_time = models.TimeField(blank=True, null=True, default=None)
    end_time = models.TimeField(blank=True, null=True, default=None)


