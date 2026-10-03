from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Pet, AdoptionRequest, Favorite


class PetBusinessLogicTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='tester1', password='password123')
        self.user2 = User.objects.create_user(username='tester2', password='password123')
        self.admin = User.objects.create_superuser(username='admin_test', password='password123')

        self.pet_available = Pet.objects.create(
            name='Buddy',
            animal_type='Dog',
            breed='Labrador',
            age=2,
            gender='Male',
            location='Dhaka',
            description='Friendly lab',
            status='Available'
        )

        self.pet_adopted = Pet.objects.create(
            name='Whiskers',
            animal_type='Cat',
            breed='Siamese',
            age=3,
            gender='Female',
            location='Dhaka',
            description='Lovely cat',
            status='Adopted'
        )

    def test_rule_1_cannot_adopt_already_adopted_pet(self):
        """Rule 1: Only available pets can be adopted. If status=Adopted, cannot submit application."""
        req = AdoptionRequest(
            user=self.user1,
            pet=self.pet_adopted,
            phone='12345678',
            address='Dhaka',
            reason='I love cats'
        )
        with self.assertRaises(ValidationError):
            req.clean()

    def test_rule_2_user_cannot_submit_duplicate_active_requests(self):
        """Rule 2: One user cannot submit multiple active requests for the same pet."""
        req1 = AdoptionRequest.objects.create(
            user=self.user1,
            pet=self.pet_available,
            phone='12345678',
            address='Dhaka',
            reason='First request',
            status='Pending'
        )

        # Attempt to create second request while first is still pending
        req2 = AdoptionRequest(
            user=self.user1,
            pet=self.pet_available,
            phone='87654321',
            address='Dhaka',
            reason='Second duplicate request',
            status='Pending'
        )
        with self.assertRaises(ValidationError):
            req2.clean()

    def test_rule_3_approved_application_updates_pet_and_closes_other_requests(self):
        """
        Rule 3: Approved application - When admin approves:
        Adoption Request -> Approved
        Pet Status -> Adopted
        Other pending requests for that pet are closed/rejected.
        """
        req_user1 = AdoptionRequest.objects.create(
            user=self.user1,
            pet=self.pet_available,
            phone='111111',
            address='Dhaka',
            reason='User 1 wants Buddy',
            status='Pending'
        )

        req_user2 = AdoptionRequest.objects.create(
            user=self.user2,
            pet=self.pet_available,
            phone='222222',
            address='Dhaka',
            reason='User 2 also wants Buddy',
            status='Pending'
        )

        # Admin approves user1's request
        req_user1.status = 'Approved'
        req_user1.save()

        # Check Pet status is now Adopted
        self.pet_available.refresh_from_db()
        self.assertEqual(self.pet_available.status, 'Adopted')

        # Check user2's request was automatically rejected
        req_user2.refresh_from_db()
        self.assertEqual(req_user2.status, 'Rejected')


class PetViewsAndTemplatesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='john', password='password123')
        self.pet = Pet.objects.create(
            name='Rocky',
            animal_type='Dog',
            breed='Boxer',
            age=1,
            gender='Male',
            location='Dhaka',
            description='Enthusiastic boxer',
            status='Available'
        )

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PawHaven')
        self.assertContains(response, 'Rocky')

    def test_pet_list_and_search(self):
        response = self.client.get('/pets/?search=Rocky')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')

        # Filter by animal_type
        response = self.client.get('/pets/?animal_type=Dog')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')

        # Negative filter
        response = self.client.get('/pets/?animal_type=Bird')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Rocky')

    def test_pet_detail_page(self):
        response = self.client.get(f'/pets/{self.pet.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')
        self.assertContains(response, 'Apply for Adoption')

    def test_adopted_pet_shows_notice_and_no_button(self):
        self.pet.status = 'Adopted'
        self.pet.save()

        response = self.client.get(f'/pets/{self.pet.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This pet has already been adopted')
        self.assertNotContains(response, 'Apply for Adoption')

    def test_pawmatch_quiz_page(self):
        response = self.client.get('/pawmatch-quiz/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PawMatch Compatibility Quiz')

        # Submit quiz
        post_data = {
            'preferred_type': 'Dog',
            'living_space': 'House',
            'activity_level': 'High',
            'has_kids': 'yes',
            'has_pets': 'no',
        }
        response = self.client.post('/pawmatch-quiz/', data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Match Analysis Complete')


class RestAPITests(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(username='api_user', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.staff_user = User.objects.create_superuser(username='staff_api', password='password123')
        self.staff_token = Token.objects.create(user=self.staff_user)

        self.pet = Pet.objects.create(
            name='Simba',
            animal_type='Cat',
            breed='Tabby',
            age=2,
            gender='Male',
            location='Dhaka',
            description='Curious tabby cat',
            status='Available'
        )

    def test_get_pets_api(self):
        response = self.api_client.get('/api/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Simba')

    def test_filter_pets_api(self):
        response = self.api_client.get('/api/pets/?animal_type=Cat')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.api_client.get('/api/pets/?animal_type=Dog')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_post_adoption_api(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        payload = {
            'pet': self.pet.id,
            'phone': '+880 1712-345678',
            'address': 'Gulshan 2, Dhaka',
            'reason': 'Looking for a lovely pet',
            'previous_pet_experience': True,
            'message': 'Can visit on Sunday'
        }
        response = self.api_client.post('/api/adoptions/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Pending')
        self.assertEqual(response.data['pet_name'], 'Simba')

        # Test Rule 2 via API (Prevent duplicate)
        response_dup = self.api_client.post('/api/adoptions/', payload)
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_auth_endpoint(self):
        response = self.api_client.post('/api/auth/token/', {
            'username': 'api_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.token.key)
