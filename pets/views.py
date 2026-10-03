from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Pet, AdoptionRequest, Favorite
from .forms import AdoptionRequestForm, PetFilterForm


def home(request):
    """Landing page featuring search hero, category shortcuts, featured pets, and metrics."""
    available_pets = Pet.objects.filter(status='Available')
    recent_pets = available_pets[:6]
    
    # Categories with count
    category_counts = {
        'Dog': Pet.objects.filter(animal_type='Dog', status='Available').count(),
        'Cat': Pet.objects.filter(animal_type='Cat', status='Available').count(),
        'Bird': Pet.objects.filter(animal_type='Bird', status='Available').count(),
        'Rabbit': Pet.objects.filter(animal_type='Rabbit', status='Available').count(),
        'Other': Pet.objects.filter(animal_type='Other', status='Available').count(),
    }

    # Platform statistics
    total_adopted = Pet.objects.filter(status='Adopted').count()
    total_available = available_pets.count()
    total_requests = AdoptionRequest.objects.count()

    # User's favorited pet IDs
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('pet_id', flat=True))

    context = {
        'recent_pets': recent_pets,
        'category_counts': category_counts,
        'total_adopted': total_adopted,
        'total_available': total_available,
        'total_requests': total_requests,
        'user_favorites': user_favorites,
    }
    return render(request, 'pets/home.html', context)


def pet_list(request):
    """
    Pet browsing page with search, filters, and pagination.
    Supports filtering by: Pet name, Animal type, Breed, Gender, Location, Adoption status.
    """
    pets_qs = Pet.objects.all()

    search_query = request.GET.get('search', '').strip()
    animal_type = request.GET.get('animal_type', '').strip()
    breed = request.GET.get('breed', '').strip()
    gender = request.GET.get('gender', '').strip()
    location = request.GET.get('location', '').strip()
    status = request.GET.get('status', '').strip()

    # Search filter (name, breed, location, description)
    if search_query:
        pets_qs = pets_qs.filter(
            Q(name__icontains=search_query) |
            Q(breed__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Specific filters
    if animal_type:
        pets_qs = pets_qs.filter(animal_type__iexact=animal_type)
    if breed:
        pets_qs = pets_qs.filter(breed__icontains=breed)
    if gender:
        pets_qs = pets_qs.filter(gender__iexact=gender)
    if location:
        pets_qs = pets_qs.filter(location__icontains=location)
    if status:
        pets_qs = pets_qs.filter(status__iexact=status)

    # Distinct locations and breeds for filter dropdowns
    all_locations = Pet.objects.values_list('location', flat=True).distinct()
    all_animal_types = ['Dog', 'Cat', 'Bird', 'Rabbit', 'Other']

    # Pagination: 6 pets per page
    paginator = Paginator(pets_qs, 6)
    page_number = request.GET.get('page', 1)
    
    try:
        pets_page = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        pets_page = paginator.get_page(1)

    # User favorite IDs
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('pet_id', flat=True))

    context = {
        'pets': pets_page,
        'search_query': search_query,
        'selected_animal_type': animal_type,
        'selected_gender': gender,
        'selected_location': location,
        'selected_status': status,
        'selected_breed': breed,
        'all_locations': all_locations,
        'all_animal_types': all_animal_types,
        'total_results': pets_qs.count(),
        'user_favorites': user_favorites,
    }
    return render(request, 'pets/pet_list.html', context)


def pet_detail(request, pk):
    """
    Pet Details Page:
    Displays pet details, images, health badges, and adoption CTA.
    If adopted, disables the button and informs the user.
    """
    pet = get_object_or_404(Pet, pk=pk)
    
    # Check if current user already submitted an application
    user_application = None
    has_active_request = False
    is_favorited = False

    if request.user.is_authenticated:
        user_application = AdoptionRequest.objects.filter(user=request.user, pet=pet).first()
        if user_application and user_application.status in ['Pending', 'Approved']:
            has_active_request = True
        is_favorited = Favorite.objects.filter(user=request.user, pet=pet).exists()

    # Similar pets
    similar_pets = Pet.objects.filter(animal_type=pet.animal_type).exclude(pk=pet.pk)[:3]

    context = {
        'pet': pet,
        'user_application': user_application,
        'has_active_request': has_active_request,
        'is_favorited': is_favorited,
        'similar_pets': similar_pets,
    }
    return render(request, 'pets/pet_detail.html', context)


@login_required
def adopt_pet(request, pk):
    """
    Adoption Application Page:
    Enforces Rule 1 (pet must be available) and Rule 2 (no duplicate active requests).
    """
    pet = get_object_or_404(Pet, pk=pk)

    # Rule 1 — Only available pets can be adopted
    if pet.status != 'Available':
        messages.error(request, f"❌ '{pet.name}' has already been adopted and is no longer available.")
        return redirect('pet_detail', pk=pet.pk)

    # Rule 2 — One user cannot submit multiple active requests for the same pet
    existing_request = AdoptionRequest.objects.filter(
        user=request.user,
        pet=pet,
        status__in=['Pending', 'Approved']
    ).first()

    if existing_request:
        messages.warning(
            request, 
            f"⚠️ You already have an active application ({existing_request.status}) for {pet.name}. Check your dashboard."
        )
        return redirect('my_adoptions')

    if request.method == 'POST':
        form = AdoptionRequestForm(request.POST, pet=pet, user=request.user)
        if form.is_valid():
            adoption_req = form.save(commit=False)
            adoption_req.user = request.user
            adoption_req.pet = pet
            adoption_req.status = 'Pending'
            adoption_req.save()
            
            messages.success(
                request, 
                f"🎉 Application submitted for {pet.name}! Our shelter team will review your details shortly."
            )
            return redirect('my_adoptions')
        else:
            messages.error(request, "Please correct the errors in your adoption application.")
    else:
        form = AdoptionRequestForm(pet=pet, user=request.user)

    return render(request, 'pets/adopt_form.html', {'pet': pet, 'form': form})


@login_required
def my_adoptions(request):
    """
    User Dashboard:
    Displays user's adoption requests with dates, statuses, and review progression.
    """
    status_filter = request.GET.get('status', '').capitalize()
    requests_qs = AdoptionRequest.objects.filter(user=request.user)

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        requests_qs = requests_qs.filter(status=status_filter)

    total_count = AdoptionRequest.objects.filter(user=request.user).count()
    pending_count = AdoptionRequest.objects.filter(user=request.user, status='Pending').count()
    approved_count = AdoptionRequest.objects.filter(user=request.user, status='Approved').count()
    rejected_count = AdoptionRequest.objects.filter(user=request.user, status='Rejected').count()

    context = {
        'applications': requests_qs,
        'status_filter': status_filter,
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'pets/my_adoptions.html', context)


@login_required
def cancel_adoption(request, pk):
    """Allows applicant to withdraw a pending application."""
    adoption_req = get_object_or_404(AdoptionRequest, pk=pk, user=request.user)
    if adoption_req.status == 'Pending':
        pet_name = adoption_req.pet.name
        adoption_req.delete()
        messages.info(request, f"Your adoption request for {pet_name} has been cancelled.")
    else:
        messages.error(request, "Only pending requests can be cancelled.")
    return redirect('my_adoptions')


@login_required
def toggle_favorite(request, pk):
    """Bonus feature: Add or remove a pet from user's favorites."""
    pet = get_object_or_404(Pet, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, pet=pet).first()

    if favorite:
        favorite.delete()
        favorited = False
        msg = f"Removed {pet.name} from your favorites."
    else:
        Favorite.objects.create(user=request.user, pet=pet)
        favorited = True
        msg = f"Added {pet.name} to your favorites! ❤️"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'favorited': favorited, 'message': msg})

    messages.success(request, msg)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('pet_detail', pk=pk)


@login_required
def my_favorites(request):
    """Bonus feature: Page listing all user's favorite pets."""
    favorites = Favorite.objects.filter(user=request.user).select_related('pet')
    pets = [f.pet for f in favorites]
    user_favorites = [f.pet_id for f in favorites]

    return render(request, 'pets/my_favorites.html', {
        'pets': pets,
        'user_favorites': user_favorites
    })


def compatibility_quiz(request):
    """
    UNIQUE FEATURE: PawMatch Compatibility Quiz
    Takes user lifestyle parameters and computes match compatibility scores for available pets.
    """
    matched_pets = []
    has_results = False

    if request.method == 'POST':
        has_results = True
        living_space = request.POST.get('living_space', 'Apartment')
        activity_level = request.POST.get('activity_level', 'Moderate')
        has_kids = request.POST.get('has_kids') == 'yes'
        has_pets = request.POST.get('has_pets') == 'yes'
        preferred_type = request.POST.get('preferred_type', 'Any')

        candidates = Pet.objects.filter(status='Available')
        if preferred_type != 'Any':
            candidates = candidates.filter(animal_type=preferred_type)

        scored = []
        for pet in candidates:
            score = 60 # Base score

            # Space matching
            if living_space == 'Apartment' and (pet.size == 'Small' or pet.animal_type in ['Cat', 'Bird', 'Rabbit']):
                score += 15
            elif living_space == 'House' and pet.size in ['Medium', 'Small']:
                score += 15
            elif living_space == 'Yard':
                score += 15

            # Activity matching
            if activity_level == pet.energy_level:
                score += 15
            elif activity_level == 'Moderate':
                score += 10

            # Kids safety
            if has_kids:
                if pet.good_with_kids:
                    score += 10
                else:
                    score -= 20

            # Other pets safety
            if has_pets:
                if pet.good_with_pets:
                    score += 10
                else:
                    score -= 15

            score = min(score, 99)
            scored.append((score, pet))

        scored.sort(key=lambda x: x[0], reverse=True)
        matched_pets = scored[:6]

    return render(request, 'pets/quiz.html', {
        'has_results': has_results,
        'matched_pets': matched_pets
    })


def api_docs(request):
    """
    UNIQUE FEATURE: Interactive REST API Documentation Portal
    Provides full interactive reference for all DRF API endpoints with examples and copyable tokens.
    """
    user_token = None
    if request.user.is_authenticated:
        token, _ = Favorite.objects.none(), None
        from rest_framework.authtoken.models import Token
        t, _ = Token.objects.get_or_create(user=request.user)
        user_token = t.key

    return render(request, 'pets/api_docs.html', {'user_token': user_token})
