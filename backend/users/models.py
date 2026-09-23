from django.contrib.auth.models import AbstractUser
from django.db import models


# contains roles namely Employee,HR Manager,HR Payroll User, HR Payroll Manager, Admin
class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"  # their own information
        HR_MANAGER = (
            "HR_MANAGER",
            "HR Manager",
        )  # responsible for employee, contract, attendance, schedule, timeoff
        HR_PAYROLL_USER = (
            "HR_PAYROLL_USER",
            "HR Payroll User",
        )  # read only access to salary config
        HR_PAYROLL_MANAGER = (
            "HR_PAYROLL_MANAGER",
            "HR Payroll Manager",
        )  # access to payroll + salary config
        ADMIN = "ADMIN", "Admin"  # access to all modules

    email = models.EmailField(unique=True)

    # determines which user is allowed to perform what operations
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
