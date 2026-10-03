from rest_framework import serializers
from django.contrib.auth.models import User
from pets.models import Pet, AdoptionRequest, Favorite


class PetSerializer(serializers.ModelSerializer):
    age_display = serializers.ReadOnlyField()

    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'animal_type', 'breed', 'age', 'age_display',
            'gender', 'location', 'description', 'image', 'status',
            'is_vaccinated', 'is_neutered', 'is_microchipped',
            'good_with_kids', 'good_with_pets', 'size', 'energy_level',
            'rescue_story', 'created_at'
        ]
        read_only_fields = ['created_at']


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    pet_name = serializers.ReadOnlyField(source='pet.name')
    pet_type = serializers.ReadOnlyField(source='pet.animal_type')
    pet_breed = serializers.ReadOnlyField(source='pet.breed')

    class Meta:
        model = AdoptionRequest
        fields = [
            'id', 'user', 'user_username', 'pet', 'pet_name', 'pet_type', 'pet_breed',
            'phone', 'address', 'reason', 'previous_pet_experience',
            'message', 'status', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        pet = attrs.get('pet') or (self.instance.pet if self.instance else None)

        # On Creation
        if not self.instance:
            if not pet:
                raise serializers.ValidationError({"pet": "Pet is required."})

            # Rule 1 — Only available pets can be adopted
            if pet.status != 'Available':
                raise serializers.ValidationError({
                    "pet": f"'{pet.name}' is already {pet.status.lower()} and no longer accepting adoption applications."
                })

            # Rule 2 — One user cannot submit multiple active requests for the same pet
            existing = AdoptionRequest.objects.filter(
                user=user,
                pet=pet,
                status__in=['Pending', 'Approved']
            ).first()
            if existing:
                raise serializers.ValidationError(
                    f"You already have an active ({existing.status}) adoption request for '{pet.name}'."
                )

        # On Update: Non-staff cannot change status or admin notes
        if self.instance and not user.is_staff:
            if 'status' in attrs and attrs['status'] != self.instance.status:
                raise serializers.ValidationError({
                    "status": "Only shelter administrators can change the adoption request status."
                })
            if 'admin_notes' in attrs and attrs['admin_notes'] != self.instance.admin_notes:
                raise serializers.ValidationError({
                    "admin_notes": "Only administrators can edit admin notes."
                })

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'Pending'
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    pet_details = PetSerializer(source='pet', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'pet', 'pet_details', 'created_at']
        read_only_fields = ['user', 'created_at']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
