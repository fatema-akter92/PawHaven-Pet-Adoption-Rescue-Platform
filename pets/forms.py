from django import forms
from .models import AdoptionRequest, Pet


class AdoptionRequestForm(forms.ModelForm):
    previous_pet_experience = forms.ChoiceField(
        choices=[(True, 'Yes, I have owned pets before'), (False, 'No, this will be my first pet')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Have you owned a pet before?",
        initial=False
    )

    class Meta:
        model = AdoptionRequest
        fields = ['phone', 'address', 'reason', 'previous_pet_experience', 'message']
        labels = {
            'phone': 'Phone Number',
            'address': 'Residential Address',
            'reason': 'Why do you want this pet?',
            'message': 'Additional Message (Optional)',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +880 1712-345678',
                'required': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your home address, City, Country',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us why you would be a great parent for this pet and about your home environment...',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any questions, preferred pickup times, or comments for the shelter team...'
            }),
        }

    def __init__(self, *args, pet=None, user=None, **kwargs):
        self.pet = pet
        self.user = user
        super().__init__(*args, **kwargs)
        if pet is not None:
            self.instance.pet = pet
        if user is not None:
            self.instance.user = user

    def clean_previous_pet_experience(self):
        val = self.cleaned_data.get('previous_pet_experience')
        return val in [True, 'True', 'true', 1, '1']

    def clean(self):
        cleaned_data = super().clean()
        if not self.pet:
            return cleaned_data

        # Rule 1 — Only available pets can be adopted
        if self.pet.status != 'Available':
            raise forms.ValidationError(
                f"❌ Sorry, '{self.pet.name}' is already {self.pet.status.lower()} and no longer accepts adoption requests."
            )

        # Rule 2 — One user cannot submit multiple active requests for the same pet
        if self.user and self.user.is_authenticated:
            existing_active = AdoptionRequest.objects.filter(
                user=self.user,
                pet=self.pet,
                status__in=['Pending', 'Approved']
            )
            if existing_active.exists():
                curr_status = existing_active.first().status
                raise forms.ValidationError(
                    f"⚠️ You already have an active request ({curr_status}) for {self.pet.name}. You cannot submit duplicate requests."
                )

        return cleaned_data


class PetFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, breed, or keyword...'
        })
    )
    animal_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Animal Types')] + Pet.ANIMAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genders')] + Pet.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location (e.g. Dhaka)'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Pet.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
