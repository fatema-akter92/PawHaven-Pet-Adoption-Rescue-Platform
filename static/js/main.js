/* ==========================================================================
   PawHaven - Client JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. AJAX Favorite Toggling
    const favButtons = document.querySelectorAll('.js-fav-btn');
    favButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const petId = btn.getAttribute('data-pet-id');
            const url = `/pets/${petId}/favorite/?format=json`;

            try {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.status === 403 || response.redirected) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                    return;
                }

                if (response.ok) {
                    const data = await response.json();
                    if (data.favorited) {
                        btn.classList.add('active');
                        btn.innerHTML = '❤️';
                    } else {
                        btn.classList.remove('active');
                        btn.innerHTML = '🤍';
                    }

                    // Optional toast notification
                    showToast(data.message);
                }
            } catch (err) {
                console.error('Favorite error:', err);
            }
        });
    });

    // 2. Clipboard Copy Helper
    window.copyToClipboard = function(text, elementId) {
        navigator.clipboard.writeText(text).then(() => {
            const el = document.getElementById(elementId);
            if (el) {
                const orig = el.innerText;
                el.innerText = 'Copied! ✓';
                el.classList.add('btn-success');
                setTimeout(() => {
                    el.innerText = orig;
                    el.classList.remove('btn-success');
                }, 2000);
            }
            showToast('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    };

    // 3. Simple Toast Notification
    function showToast(message) {
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.position = 'fixed';
            toastContainer.style.bottom = '20px';
            toastContainer.style.right = '20px';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.style.background = '#622CD1';
        toast.style.color = '#FFFFFF';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '9999px';
        toast.style.boxShadow = '0 10px 25px rgba(98, 44, 209, 0.3)';
        toast.style.marginBottom = '10px';
        toast.style.fontSize = '0.9rem';
        toast.style.fontWeight = '600';
        toast.style.transition = 'all 0.3s ease';
        toast.innerText = message;

        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 2800);
    }
});
