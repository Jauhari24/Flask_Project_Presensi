// static/js/modals.js

function showModal(message, iconType = "info") {
    const modal = document.getElementById('custom-modal');
    const messageEl = document.getElementById('modal-message');
    const iconEl = document.getElementById('modal-icon');
    const okBtn = document.getElementById('modal-ok-btn');

    messageEl.textContent = message;

    // Ganti ikon berdasarkan tipe
    if (iconType === "success") {
        iconEl.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>`;
        iconEl.className = "mx-auto mb-4 w-12 h-12 text-green-500";
    } else if (iconType === "error") {
        iconEl.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>`;
        iconEl.className = "mx-auto mb-4 w-12 h-12 text-red-500";
    } else {
        iconEl.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12c0 4.97-4.03 9-9 9S3 16.97 3 12 7.03 3 12 3s9 4.03 9 9z"/>`;
        iconEl.className = "mx-auto mb-4 w-12 h-12 text-gray-400";
    }

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    okBtn.onclick = () => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    };
}

function showConfirmModal(message, onConfirm) {
    const modal = document.getElementById('confirm-modal');
    const messageEl = document.getElementById('confirm-modal-message');
    const yesBtn = document.getElementById('confirm-yes-btn');
    const noBtn = document.getElementById('confirm-no-btn');

    messageEl.textContent = message;
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    // Reset event handler agar tidak double
    const newYesBtn = yesBtn.cloneNode(true);
    yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);

    newYesBtn.onclick = () => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        onConfirm();
    };

    noBtn.onclick = () => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    };
}

// static/js/toast.js
// Show a toast notification

function showToast(message, type = "info", duration = 3000) {
    const toast = document.getElementById("custom-toast");
    const messageEl = document.getElementById("toast-message");
    const iconEl = document.getElementById("toast-icon");

    messageEl.textContent = message;

    // Set icon & color
    if (type === "success") {
        iconEl.innerHTML = `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>`;
        iconEl.className = "inline-flex items-center justify-center w-8 h-8 text-green-500 bg-green-100 rounded-lg dark:bg-green-800 dark:text-green-200";
    } else if (type === "error") {
        iconEl.innerHTML = `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>`;
        iconEl.className = "inline-flex items-center justify-center w-8 h-8 text-red-500 bg-red-100 rounded-lg dark:bg-red-800 dark:text-red-200";
    } else {
        iconEl.innerHTML = `<svg class="w-4 h-4" fill="none" viewBox="0 0 18 20" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.147 15.085a7.159 7.159 0 0 1-6.189 3.307A6.713 6.713 0 0 1 3.1 15.444c-2.679-4.513.287-8.737.888-9.548..." />
        </svg>`;
        iconEl.className = "inline-flex items-center justify-center w-8 h-8 text-blue-500 bg-blue-100 rounded-lg dark:bg-blue-800 dark:text-blue-200";
    }

    toast.classList.remove("hidden");

    // Hide after duration
    setTimeout(() => {
        toast.classList.add("hidden");
    }, duration);
}

function hideToast() {
    const toast = document.getElementById("custom-toast");
    toast.classList.add("hidden");
}