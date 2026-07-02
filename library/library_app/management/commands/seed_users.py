from django.core.management.base import BaseCommand

from library_app.models import User

SEED_USERS = [
    {
        "username": "alice",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Anderson",
        "password": "Str0ngPassw0rd!",
        "role": User.Role.LIBRARIAN,
    },
    {
        "username": "bob",
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Brown",
        "password": "Str0ngPassw0rd!",
        "role": User.Role.STUDENT,
    },
    {
        "username": "carol",
        "email": "carol@example.com",
        "first_name": "Carol",
        "last_name": "Clark",
        "password": "Str0ngPassw0rd!",
        "role": User.Role.STUDENT,
    },
    {
        "username": "dave",
        "email": "dave@example.com",
        "first_name": "Dave",
        "last_name": "Davis",
        "password": "Str0ngPassw0rd!",
        "role": User.Role.STUDENT,
    },
]


class Command(BaseCommand):
    help = "Seeds a handful of demo users (idempotent: skips users that already exist)."

    def handle(self, *args, **options):
        created_count = 0
        for data in SEED_USERS:
            if User.objects.filter(username=data["username"]).exists():
                self.stdout.write(f"Skipping '{data['username']}' (already exists).")
                continue

            user = User(
                username=data["username"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
            )
            user.set_password(data["password"])
            user.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created user '{user.username}' ({user.role})."))

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} user(s) created."))
