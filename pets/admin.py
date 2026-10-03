from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe 
from .models import Pet, AdoptionRequest, Favorite


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview', 
        'name', 
        'animal_type', 
        'breed', 
        'age_display', 
        'gender', 
        'location', 
        'status_badge', 
        'created_at'
    )
    list_filter = ('animal_type', 'status', 'gender', 'location')
    search_fields = ('name', 'breed', 'location', 'description')
    list_editable = ()
    readonly_fields = ('created_at', 'image_display_large')
    actions = ['mark_as_available', 'mark_as_adopted']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'animal_type', 'breed', 'age', 'gender', 'location', 'status')
        }),
        ('Details & Image', {
            'fields': ('description', 'image', 'image_display_large', 'rescue_story')
        }),
        ('Health & Compatibility (Unique Features)', {
            'fields': (
                'size', 'energy_level',
                'is_vaccinated', 'is_neutered', 'is_microchipped',
                'good_with_kids', 'good_with_pets'
            )
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px; border: 2px solid #ddd6fe;" />',
                obj.image.url
            )
        return mark_safe('<span style="color: #9ca3af; font-size: 11px;">No image</span>')
    image_preview.short_description = 'Photo'

    def image_display_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 12px; border: 3px solid #c4b5fd;" />',
                obj.image.url
            )
        return "No image uploaded yet"
    image_display_large.short_description = 'Current Photo'

    # ✅ এখানে mark_safe ব্যবহার করা হয়েছে
    def status_badge(self, obj):
        if obj.status == 'Available':
            return mark_safe(
                '<span style="background-color: #ede9fe; color: #6d28d9; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #c4b5fd;">🐾 Available</span>'
            )
        return mark_safe(
            '<span style="background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #fca5a5;">❤️ Adopted</span>'
        )
    status_badge.short_description = 'Status'

    @admin.action(description="Mark selected pets as Available")
    def mark_as_available(self, request, queryset):
        count = queryset.update(status='Available')
        self.message_user(request, f"{count} pet(s) marked as Available.")

    @admin.action(description="Mark selected pets as Adopted")
    def mark_as_adopted(self, request, queryset):
        count = queryset.update(status='Adopted')
        self.message_user(request, f"{count} pet(s) marked as Adopted.")


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'user_display', 
        'pet_display', 
        'phone', 
        'status_badge', 
        'created_at'
    )
    list_filter = ('status', 'pet__animal_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'pet__name', 'phone', 'address', 'reason')
    readonly_fields = ('user', 'pet', 'created_at', 'updated_at')
    actions = ['approve_adoption_requests', 'reject_adoption_requests']

    fieldsets = (
        ('Adoption Information', {
            'fields': ('user', 'pet', 'phone', 'address')
        }),
        ('Applicant Answers', {
            'fields': ('previous_pet_experience', 'reason', 'message')
        }),
        ('Shelter Review & Decision', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_display(self, obj):
        return format_html('<strong>{}</strong> <br/><span style="color:#6b7280; font-size:11px;">{}</span>', obj.user.username, obj.user.email or "No email")
    user_display.short_description = 'Applicant'

    def pet_display(self, obj):
        return format_html('<strong>{}</strong> <br/><span style="color:#7c3aed; font-size:11px;">{} ({})</span>', obj.pet.name, obj.pet.animal_type, obj.pet.breed)
    pet_display.short_description = 'Requested Pet'

    # ✅ এখানে format_html এর বদলে mark_safe ব্যবহার করা হয়েছে
    def status_badge(self, obj):
        if obj.status == 'Pending':
            return mark_safe(
                '<span style="background-color: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #fcd34d;">⏳ Pending</span>'
            )
        elif obj.status == 'Approved':
            return mark_safe(
                '<span style="background-color: #d1fae5; color: #065f46; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #6ee7b7;">✅ Approved</span>'
            )
        return mark_safe(
            '<span style="background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #fca5a5;">❌ Rejected</span>'
        )
    status_badge.short_description = 'Status'

    @admin.action(description="✅ Approve selected requests (Mark Pet as Adopted)")
    def approve_adoption_requests(self, request, queryset):
        count = 0
        for adoption in queryset:
            adoption.status = 'Approved'
            adoption.admin_notes = "Approved via admin console."
            adoption.save()  # Triggers Rule 3 logic in save()
            count += 1
        self.message_user(request, f"{count} request(s) approved. Associated pets have been marked as Adopted.")

    @admin.action(description="❌ Reject selected requests")
    def reject_adoption_requests(self, request, queryset):
        count = queryset.update(status='Rejected', admin_notes="Rejected via admin console.")
        self.message_user(request, f"{count} request(s) rejected.")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'pet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'pet__name')