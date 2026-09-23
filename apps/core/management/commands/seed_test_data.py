import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from apps.properties.models import Property, Amenity
from apps.listings.models import Listing, ListingPhoto
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.core.models import LodgingType

fake = Faker('de_DE')

User = get_user_model()

GERMAN_CITIES = [
    ("Berlin", "Berlin"),
    ("München", "Bayern"),
    ("Hamburg", "Hamburg"),
    ("Köln", "Nordrhein-Westfalen"),
    ("Frankfurt am Main", "Hessen"),
    ("Stuttgart", "Baden-Württemberg"),
    ("Düsseldorf", "Nordrhein-Westfalen"),
    ("Leipzig", "Sachsen")
]

COMMON_AMENITIES = [
    "Wi-Fi", "Washing Machine", "Air Conditioning", "Kitchen",
    "Elevator", "Parking", "Workspace", "TV", "Heating"
]


class Command(BaseCommand):
    help = "Seed database with logically valid German data"

    def handle(self, *args, **options):
        self.stdout.write("Start seeding database with logically valid German data...")

        amenity_objects = []
        for name in COMMON_AMENITIES:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            amenity_objects.append(amenity)
        self.stdout.write(f"Generated {len(amenity_objects)} amenities.")

        users = []

        if not User.objects.filter(is_staff=True).exists():
            User.objects.create_superuser(
                email="admin@rent.de",
                password="password123",
                first_name="Admin",
                last_name="System"
            )
            self.stdout.write("Created superuser: admin@rent.de")

        for i in range(10):
            email = f"user{i}@rent.de"
            User.objects.filter(email=email).hard_delete()

            user = User.objects.create_user(
                email=email,
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=f"+4915{random.randint(10000000, 99999999)}",
                date_of_birth=date(1985, 1, 1) + timedelta(days=random.randint(0, 7000)),
                bio=fake.sentence(nb_words=10),
                is_email_verified=True
            )
            users.append(user)
        self.stdout.write(f"Generated {len(users)} users with password: 'password123'")

        today = date.today()
        listings = []

        for i, owner in enumerate(users):
            for _ in range(random.randint(1, 2)):
                city, state = random.choice(GERMAN_CITIES)
                lodging_type = random.choice(LodgingType.choices)[0]

                apt_num = ""
                room_num = ""
                if lodging_type == LodgingType.APARTMENT:
                    apt_num = str(random.randint(1, 150))
                elif lodging_type == LodgingType.COMMUNAL:
                    apt_num = str(random.randint(1, 50))
                    room_num = str(random.randint(1, 6))

                total_area = Decimal(random.randint(40, 150))
                living_area = total_area - Decimal(random.randint(10, 30))

                prop = Property.objects.create(
                    owner=owner,
                    is_verified=True,
                    country="Germany",
                    state=state,
                    city=city,
                    street=fake.street_name(),
                    building=str(random.randint(1, 120)),
                    apartment_number=apt_num,
                    room_number=room_num,
                    lodging_type=lodging_type,
                    total_rooms_count=random.randint(3, 6),
                    bedrooms_count=random.randint(1, 3),
                    bathrooms_count=random.randint(1, 2),
                    kitchens_count=1,
                    total_area=total_area,
                    living_area=living_area
                )
                prop.amenities.set(random.sample(amenity_objects, k=random.randint(3, 6)))

                listing = Listing.objects.create(
                    title=f"Beautiful {lodging_type.title()} in {city}",
                    description=fake.paragraph(nb_sentences=3),
                    property=prop,
                    price_per_night=Decimal(random.randint(45, 250)),
                    max_guests=random.randint(2, 6),
                    min_rental_days=random.randint(1, 3),
                    is_active=True
                )

                ListingPhoto.objects.create(
                    listing=listing,
                    photo="listing_photos/default.jpg",
                    photo_sequence_number=1
                )
                listings.append(listing)

        self.stdout.write(f"Generated {len(listings)} verified properties and public listings.")

        self.stdout.write("Generating transactional bookings & historical reviews...")

        for listing in listings:
            host = listing.property.owner
            potential_lessees = [u for u in users if u != host]

            if not potential_lessees:
                continue

            ended_lessee = random.choice(potential_lessees)
            past_check_in = today - timedelta(days=12)
            past_check_out = today - timedelta(days=5)

            Booking.objects.create(
                listing=listing,
                lessee=ended_lessee,
                check_in=past_check_in,
                check_out=past_check_out,
                status=Booking.Status.ENDED,
                amount_paid=listing.price_per_night * 7,
                lessee_comment="Looking forward to visiting Germany!",
                lessor_comment="Welcome!"
            )

            Review.objects.create(
                listing=listing,
                commentator=ended_lessee,
                review=random.choice([
                    "Wonderful place! Clean, quiet, and very close to the center. Highly recommended!",
                    "Great host, very quick communication. The apartment fully matches the photos.",
                    "Good value for money. Had some minor issues with Wi-Fi, but overall a nice stay."
                ]),
                rating=random.randint(4, 5)
            )

            occupied_lessee = random.choice(potential_lessees)
            Booking.objects.create(
                listing=listing,
                lessee=occupied_lessee,
                check_in=today - timedelta(days=1),
                check_out=today + timedelta(days=3),
                status=Booking.Status.OCCUPIED,
                amount_paid=listing.price_per_night * 4
            )

            requested_lessee = random.choice(potential_lessees)
            Booking.objects.create(
                listing=listing,
                lessee=requested_lessee,
                check_in=today + timedelta(days=10),
                check_out=today + timedelta(days=15),
                status=Booking.Status.REQUESTED,
                amount_paid=listing.price_per_night * 5,
                lessee_comment="Hello! We are a couple arriving for a weekend conference."
            )

        self.stdout.write("Database successfully seeded with highly consistent transaction data.")