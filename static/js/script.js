document.addEventListener('DOMContentLoaded', () => {
    console.log('TabChem Pharma Inventory UI Loaded.');
    
    // Add subtle visual feedback for editable inputs
    const editables = document.querySelectorAll('.input-editable');
    editables.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.remove('bg-transparent');
            this.classList.add('bg-white');
            this.classList.add('shadow-sm');
        });
        input.addEventListener('blur', function() {
            this.classList.add('bg-transparent');
            this.classList.remove('bg-white');
            this.classList.remove('shadow-sm');
        });
    });
});
