document.addEventListener('DOMContentLoaded', () => {
    const expandButtons = document.querySelectorAll('.expand-button');

    expandButtons.forEach(button => {
        button.addEventListener('click', () => {
            const packageId = button.getAttribute('data-package-id');
            const detailsRow = document.querySelector(`.package-details[data-package-id="${packageId}"]`);

            detailsRow.classList.toggle('hidden');
        });
    });
});