from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _  # For translatable help text

from users.management.logic import generate_dummy_users_data


class Command(BaseCommand):
    help = _(
        "Creates a specified number of dummy users with populated profiles for development and testing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, help=_("The number of dummy users to create.")
        )
        parser.add_argument(
            "--password",
            type=str,
            default="password123",  # Default password, should be documented
            help=_(
                'Define a common password for all dummy users. Default is "password123".'
            ),
        )
        # Add any other arguments you might need (e.g., --is_active, --group)
        # TODO: Add more robust arguments as we add more features to users such as email verification, groups, new profile types, etc.

    def handle(self, *args, **options):
        num_users_to_create: int = options["count"]
        common_password: str = options["password"]

        if num_users_to_create <= 0:
            raise CommandError(
                _("The number of users to create must be a positive integer.")
            )

        self.stdout.write(
            self.style.NOTICE(
                f'Attempting to create {num_users_to_create} dummy user(s) with password "{common_password}"...'
            )
        )

        try:
            created_count, failed_count = generate_dummy_users_data(
                num_users=num_users_to_create, password=common_password
            )

            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {created_count} dummy user(s)."
                    )
                )
            if failed_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to create {failed_count} dummy user(s) (check console output for details)."
                    )
                )
            if created_count == 0 and failed_count == 0:
                self.stdout.write(
                    self.style.NOTICE(
                        "No new users were processed. This might be unexpected."
                    )
                )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))

        self.stdout.write(self.style.NOTICE("Dummy user creation process finished."))
