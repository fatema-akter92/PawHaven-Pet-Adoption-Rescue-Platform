import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.authtoken.models import Token
from pets.models import Pet, AdoptionRequest, Favorite
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = 'Seeds database with realistic pets, users, adoption requests, and auth tokens.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[*] Starting database seeding..."))

        # 1. Create Media Directory
        media_pets_dir = os.path.join(settings.MEDIA_ROOT, 'pets')
        os.makedirs(media_pets_dir, exist_ok=True)

        # 2. Create Users
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pawhaven.local',
                'first_name': 'Shelter',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        Token.objects.get_or_create(user=admin_user)
        self.stdout.write(self.style.SUCCESS("[OK] Superuser created: admin / admin123"))

        # User Rahim (featured in PDF example!)
        rahim, created = User.objects.get_or_create(
            username='rahim',
            defaults={
                'email': 'rahim@example.com',
                'first_name': 'Rahim',
                'last_name': 'Chowdhury',
            }
        )
        rahim.set_password('rahim123')
        rahim.save()
        Token.objects.get_or_create(user=rahim)
        self.stdout.write(self.style.SUCCESS("[OK] Adopter created: rahim / rahim123"))

        # User Fatima
        fatima, created = User.objects.get_or_create(
            username='fatima',
            defaults={
                'email': 'fatima@example.com',
                'first_name': 'Fatima',
                'last_name': 'Begum',
            }
        )
        fatima.set_password('fatima123')
        fatima.save()
        Token.objects.get_or_create(user=fatima)
        self.stdout.write(self.style.SUCCESS("[OK] Adopter created: fatima / fatima123"))

        # User Meem (Admin)
        meem, created = User.objects.get_or_create(
            username='meem',
            defaults={
                'email': 'fatemaaktermeem838@gmail.com',
                'first_name': 'Fatema',
                'last_name': 'Akter',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        meem.is_staff = True
        meem.is_superuser = True
        meem.set_password('meem123')
        meem.save()
        Token.objects.get_or_create(user=meem)
        self.stdout.write(self.style.SUCCESS("[OK] Admin user created: meem / meem123"))

        # Helper to generate aesthetic pet banner images
        def generate_pet_image(filename, name, animal_type, bg_color):
            filepath = os.path.join(media_pets_dir, filename)
            if not os.path.exists(filepath):
                img = Image.new('RGB', (640, 480), color=bg_color)
                draw = ImageDraw.Draw(img)
                
                # Decorative borders and shapes
                draw.rectangle([20, 20, 620, 460], outline=(220, 210, 255), width=6)
                draw.ellipse([260, 100, 380, 220], fill=(255, 255, 255))
                
                # Pet text banner
                draw.text((320, 150), animal_type[0], fill=(120, 67, 229), anchor="mm")
                draw.text((320, 270), name, fill=(50, 20, 110), anchor="mm")
                draw.text((320, 310), f"PawHaven {animal_type}", fill=(100, 80, 150), anchor="mm")
                draw.text((320, 400), "💜 Rescue with Love", fill=(140, 100, 240), anchor="mm")
                
                img.save(filepath, 'JPEG', quality=90)
            return f"pets/{filename}"

        # 3. Create Pets Catalog
        pets_data = [
            {
                'name': 'Max',
                'animal_type': 'Dog',
                'breed': 'Golden Retriever',
                'age': 2,
                'gender': 'Male',
                'location': 'Dhaka',
                'description': 'Max is friendly and playful. He gets along wonderfully with families, loves playing fetch in the garden, and is completely house-trained.',
                'status': 'Available',
                'size': 'Large',
                'energy_level': 'High',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'max.jpg',
                'bg_color': (243, 239, 255),
            },
            {
                'name': 'Luna',
                'animal_type': 'Cat',
                'breed': 'Persian Cat',
                'age': 1,
                'gender': 'Female',
                'location': 'Dhaka',
                'description': 'Luna is a gentle, affectionate Persian cat with silk-like fur. She enjoys curling up on soft cushions and watching birds from the window sill.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Low',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'luna.jpg',
                'bg_color': (245, 243, 255),
            },
            {
                'name': 'Coco',
                'animal_type': 'Dog',
                'breed': 'Beagle',
                'age': 3,
                'gender': 'Male',
                'location': 'Dhaka',
                'description': 'Coco is a curious beagle with an inquisitive nose. He has successfully found his forever home and was adopted by a loving family!',
                'status': 'Available',
                'size': 'Medium',
                'energy_level': 'Moderate',
                'good_with_kids': True,
                'good_with_pets': False,
                'img_file': 'coco.jpg',
                'bg_color': (238, 232, 255),
            },
            {
                'name': 'Milo',
                'animal_type': 'Dog',
                'breed': 'German Shepherd',
                'age': 2,
                'gender': 'Male',
                'location': 'Dhaka',
                'description': 'Milo is an exceptionally loyal and intelligent companion. He knows basic obedience commands and loves long evening jogs.',
                'status': 'Available',
                'size': 'Large',
                'energy_level': 'High',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'milo.jpg',
                'bg_color': (240, 235, 255),
            },
            {
                'name': 'Bella',
                'animal_type': 'Cat',
                'breed': 'British Shorthair',
                'age': 1,
                'gender': 'Female',
                'location': 'Chittagong',
                'description': 'Bella is a calm, independent feline with stunning copper eyes. Perfect for apartment dwellers who appreciate a tranquil presence.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Low',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'bella.jpg',
                'bg_color': (244, 238, 255),
            },
            {
                'name': 'Barnaby',
                'animal_type': 'Rabbit',
                'breed': 'Holland Lop',
                'age': 1,
                'gender': 'Male',
                'location': 'Dhaka',
                'description': 'Barnaby has floppy ears and a penchant for fresh timothy hay and coriander treats. He is gentle, quiet, and litter trained.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Low',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'barnaby.jpg',
                'bg_color': (246, 240, 255),
            },
            {
                'name': 'Rio',
                'animal_type': 'Bird',
                'breed': 'Ringneck Parakeet',
                'age': 2,
                'gender': 'Male',
                'location': 'Dhaka',
                'description': 'Rio is a vibrant green parakeet who loves whistling cheerful melodies and mimicking friendly household greetings.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Moderate',
                'good_with_kids': True,
                'good_with_pets': False,
                'img_file': 'rio.jpg',
                'bg_color': (242, 236, 255),
            },
            {
                'name': 'Daisy',
                'animal_type': 'Dog',
                'breed': 'Labrador Retriever',
                'age': 4,
                'gender': 'Female',
                'location': 'Chittagong',
                'description': 'Daisy is a sweetheart who adores belly rubs and afternoon naps. She is exceptionally patient with toddlers and other dogs.',
                'status': 'Available',
                'size': 'Large',
                'energy_level': 'Moderate',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'daisy.jpg',
                'bg_color': (240, 234, 255),
            },
            {
                'name': 'Oliver',
                'animal_type': 'Cat',
                'breed': 'Scottish Fold',
                'age': 2,
                'gender': 'Male',
                'location': 'Sylhet',
                'description': 'Oliver is a cuddly Scottish Fold with cute folded ears. He purrs like an engine whenever someone gently strokes behind his ears.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Low',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'oliver.jpg',
                'bg_color': (245, 239, 255),
            },
            {
                'name': 'Clover',
                'animal_type': 'Rabbit',
                'breed': 'Mini Rex',
                'age': 1,
                'gender': 'Female',
                'location': 'Dhaka',
                'description': 'Clover has plush velvet fur and loves binkying across the living room rug. Quiet, clean, and wonderful for indoor apartment living.',
                'status': 'Available',
                'size': 'Small',
                'energy_level': 'Moderate',
                'good_with_kids': True,
                'good_with_pets': True,
                'img_file': 'clover.jpg',
                'bg_color': (247, 241, 255),
            },
        ]

        created_pets = {}
        for p_data in pets_data:
            img_rel_path = generate_pet_image(
                p_data['img_file'], 
                p_data['name'], 
                p_data['animal_type'], 
                p_data['bg_color']
            )

            pet, _ = Pet.objects.get_or_create(
                name=p_data['name'],
                breed=p_data['breed'],
                defaults={
                    'animal_type': p_data['animal_type'],
                    'age': p_data['age'],
                    'gender': p_data['gender'],
                    'location': p_data['location'],
                    'description': p_data['description'],
                    'status': p_data['status'],
                    'size': p_data['size'],
                    'energy_level': p_data['energy_level'],
                    'good_with_kids': p_data['good_with_kids'],
                    'good_with_pets': p_data['good_with_pets'],
                    'image': img_rel_path,
                }
            )
            created_pets[pet.name] = pet

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(created_pets)} pets seeded successfully."))

        # 4. Seed Adoption Requests Matching PDF Page 4 Example!
        # Example from PDF:
        # Max -> 20 Sep -> Pending (User: Rahim)
        # Luna -> 18 Sep -> Rejected (User: Rahim)
        # Coco -> 15 Sep -> Approved (User: Rahim)
        if 'Max' in created_pets:
            AdoptionRequest.objects.get_or_create(
                user=rahim,
                pet=created_pets['Max'],
                defaults={
                    'phone': '+880 1712-345678',
                    'address': 'Dhanmondi Road 27, Dhaka',
                    'reason': 'We have a spacious house with an enclosed garden and love Golden Retrievers.',
                    'previous_pet_experience': True,
                    'message': 'We are home on weekends and can visit the shelter on Saturday.',
                    'status': 'Pending',
                    'admin_notes': 'Application received. Home inspection scheduled.',
                }
            )

        if 'Luna' in created_pets:
            AdoptionRequest.objects.get_or_create(
                user=rahim,
                pet=created_pets['Luna'],
                defaults={
                    'phone': '+880 1712-345678',
                    'address': 'Dhanmondi Road 27, Dhaka',
                    'reason': 'Wanted a companion cat.',
                    'previous_pet_experience': False,
                    'message': '',
                    'status': 'Rejected',
                    'admin_notes': 'Applicant already has dogs that may not be suitable for Luna.',
                }
            )

        if 'Coco' in created_pets:
            coco_pet = created_pets['Coco']
            if not AdoptionRequest.objects.filter(user=rahim, pet=coco_pet).exists():
                coco_pet.status = 'Available'
                coco_pet.save(update_fields=['status'])
                req = AdoptionRequest.objects.create(
                    user=rahim,
                    pet=coco_pet,
                    phone='+880 1712-345678',
                    address='Dhanmondi Road 27, Dhaka',
                    reason='Experienced beagle family looking to adopt.',
                    previous_pet_experience=True,
                    message='All family members agreed and excited.',
                    status='Pending',
                )
                req.status = 'Approved'
                req.admin_notes = 'Approved by shelter director. Adoption agreement signed.'
                req.save()

        # Fatima's sample application for Milo
        if 'Milo' in created_pets:
            AdoptionRequest.objects.get_or_create(
                user=fatima,
                pet=created_pets['Milo'],
                defaults={
                    'phone': '+880 1819-987654',
                    'address': 'Uttara Sector 7, Dhaka',
                    'reason': 'Looking for an active running companion and loving family pet.',
                    'previous_pet_experience': True,
                    'message': 'Ready for pickup anytime!',
                    'status': 'Pending',
                    'admin_notes': 'Under initial background check.',
                }
            )

        # 5. Seed Favorites
        if 'Max' in created_pets:
            Favorite.objects.get_or_create(user=rahim, pet=created_pets['Max'])
        if 'Bella' in created_pets:
            Favorite.objects.get_or_create(user=rahim, pet=created_pets['Bella'])
        if 'Luna' in created_pets:
            Favorite.objects.get_or_create(user=fatima, pet=created_pets['Luna'])

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Seeding completed successfully!"))
        self.stdout.write(self.style.SUCCESS("""
Test User Credentials:
---------------------------------------------
1. Admin:   admin   / admin123  (Superuser & Shelter Admin)
2. Adopter: rahim   / rahim123  (Has sample Pending, Approved, Rejected requests)
3. Adopter: fatima  / fatima123 (Regular adopter)
---------------------------------------------
"""))
