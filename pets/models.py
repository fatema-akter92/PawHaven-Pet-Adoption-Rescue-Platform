from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Pet(models.Model):
    ANIMAL_TYPE_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Rabbit', 'Rabbit'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Adopted', 'Adopted'),
    ]

    SIZE_CHOICES = [
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
    ]

    ENERGY_CHOICES = [
        ('Low', 'Low / Calm'),
        ('Moderate', 'Moderate'),
        ('High', 'High / Active'),
    ]

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=50, choices=ANIMAL_TYPE_CHOICES, default='Dog')
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=1, help_text="Age in years")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Male')
    location = models.CharField(max_length=100, default='Dhaka')
    description = models.TextField(help_text="Detailed description of the pet")
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

    # Unique Features: Health badges & Compatibility
    is_vaccinated = models.BooleanField(default=True, help_text="Up to date on vaccinations")
    is_neutered = models.BooleanField(default=True, help_text="Spayed or neutered")
    is_microchipped = models.BooleanField(default=True, help_text="Microchipped for identification")
    good_with_kids = models.BooleanField(default=True, help_text="Safe and friendly with children")
    good_with_pets = models.BooleanField(default=True, help_text="Sociable with other pets")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='Medium')
    energy_level = models.CharField(max_length=20, choices=ENERGY_CHOICES, default='Moderate')
    rescue_story = models.TextField(blank=True, default="Lovingly rescued and rehabilitated at our shelter.")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.animal_type} - {self.status})"

    @property
    def age_display(self):
        if self.age == 1:
            return "1 year"
        return f"{self.age} years"

    @property
    def is_available(self):
        return self.status == 'Available'


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    phone = models.CharField(max_length=30)
    address = models.TextField()
    reason = models.TextField(help_text="Why do you want to adopt this pet?")
    previous_pet_experience = models.BooleanField(
        default=False, 
        help_text="Have you owned a pet before?"
    )
    message = models.TextField(blank=True, help_text="Additional notes or questions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_notes = models.TextField(blank=True, help_text="Notes from shelter administrators")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.user.username} for {self.pet.name} [{self.status}]"

    def clean(self):
        super().clean()
        # Safely check if pet and user are attached
        has_pet = False
        try:
            has_pet = bool(getattr(self, 'pet_id', None) or hasattr(self, 'pet')) and (self.pet is not None)
        except Exception:
            has_pet = False

        has_user = False
        try:
            has_user = bool(getattr(self, 'user_id', None) or hasattr(self, 'user')) and (self.user is not None)
        except Exception:
            has_user = False

        # Rule 1: Only available pets can be adopted
        if not self.pk and has_pet:
            if self.pet.status != 'Available':
                raise ValidationError({
                    'pet': f"'{self.pet.name}' is already {self.pet.status.lower()} and not available for new adoptions."
                })

        # Rule 2: One user cannot submit multiple active requests for the same pet
        if not self.pk and has_user and has_pet:
            existing_active = AdoptionRequest.objects.filter(
                user=self.user,
                pet=self.pet,
                status__in=['Pending', 'Approved']
            )
            if existing_active.exists():
                raise ValidationError(
                    f"You already have an active ({existing_active.first().status}) adoption request for {self.pet.name}."
                )

    def save(self, *args, **kwargs):
        # Enforce model validation before saving
        self.full_clean()
        
        is_approval = self.status == 'Approved'
        super().save(*args, **kwargs)

        # Rule 3 — Approved application:
        # When admin approves an application:
        # Adoption Request -> Approved => Pet Status = Adopted
        # And other pending requests for that same pet should no longer be accepted.
        if is_approval:
            # Update pet status
            if self.pet.status != 'Adopted':
                self.pet.status = 'Adopted'
                self.pet.save(update_fields=['status'])

            # Automatically reject other pending requests for this pet
            AdoptionRequest.objects.filter(
                pet=self.pet,
                status='Pending'
            ).exclude(pk=self.pk).update(
                status='Rejected',
                admin_notes=f"Pet was adopted by {self.user.username} on {self.updated_at.strftime('%Y-%m-%d')}."
            )


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pet')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ❤️ {self.pet.name}"
