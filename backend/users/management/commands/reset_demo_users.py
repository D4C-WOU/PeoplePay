from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """
    Restore the standard PeoplePay360 development accounts.

    This command is intentionally separate from the main seed command.
    That means we can recover forgotten login passwords without recreating
    departments, employees, attendance, contracts, or payroll data.
    """

    help = "Create or reset PeoplePay360 development user accounts."

    DEMO_USERS = [
        {
            "username": "admin",
            "email": "admin@peoplepay360.com",
            "first_name": "PeoplePay",
            "last_name": "Administrator",
            "role": User.Role.ADMIN,
        },
        {
            "username": "neha",
            "email": "neha@peoplepay360.com",
            "first_name": "Neha",
            "last_name": "Mehta",
            "role": User.Role.HR_MANAGER,
        },
        {
            "username": "karan",
            "email": "karan@peoplepay360.com",
            "first_name": "Karan",
            "last_name": "Desai",
            "role": User.Role.HR_PAYROLL_MANAGER,
        },
        {
            "username": "aarav",
            "email": "aarav@peoplepay360.com",
            "first_name": "Aarav",
            "last_name": "Patel",
            "role": User.Role.EMPLOYEE,
        },
        {
            "username": "riya",
            "email": "riya@peoplepay360.com",
            "first_name": "Riya",
            "last_name": "Shah",
            "role": User.Role.EMPLOYEE,
        },
        {
            "username": "dev",
            "email": "dev@peoplepay360.com",
            "first_name": "Dev",
            "last_name": "Joshi",
            "role": User.Role.EMPLOYEE,
        },
    ]

    PASSWORD = "PeoplePay@123"

    def handle(self, *args, **options):
        self.stdout.write("Restoring PeoplePay360 development accounts...")

        for data in self.DEMO_USERS:
            username = data["username"]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": data["role"],
                },
            )

            # Keep existing user information but make sure the demo account
            # always has the expected development role and profile details.
            user.email = data["email"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.role = data["role"]

            # This is the important part: always reset the known password.
            user.set_password(self.PASSWORD)

            # Ensure the development accounts are not disabled.
            user.is_active = True

            # Give the ADMIN demo account Django superuser access as well.
            if username == "admin":
                user.is_staff = True
                user.is_superuser = True

            user.save()

            action = "created" if created else "reset"

            self.stdout.write(
                self.style.SUCCESS(f"  {action}: {username} ({data['role']})")
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("PeoplePay360 development accounts are ready.")
        )
        self.stdout.write("")
        self.stdout.write(f"Development password: {self.PASSWORD}")
