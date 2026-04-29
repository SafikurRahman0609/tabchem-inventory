document.addEventListener('DOMContentLoaded', () => {
    const previewScopes = document.querySelectorAll('[data-preview-scope]');

    previewScopes.forEach((scope) => {
        const input = scope.querySelector('[data-preview-input]');
        const previewImage = scope.querySelector('.preview-image');
        const emptyState = scope.querySelector('.preview-empty-state');

        if (!input || !previewImage || !emptyState) {
            return;
        }

        input.addEventListener('change', () => {
            const [file] = input.files || [];

            if (!file) {
                if (!previewImage.getAttribute('src')) {
                    previewImage.classList.add('d-none');
                    emptyState.classList.remove('d-none');
                }
                return;
            }

            const previewUrl = URL.createObjectURL(file);
            previewImage.src = previewUrl;
            previewImage.classList.remove('d-none');
            emptyState.classList.add('d-none');

            previewImage.onload = () => {
                URL.revokeObjectURL(previewUrl);
            };
        });
    });
});
