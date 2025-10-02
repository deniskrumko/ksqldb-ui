const deleteModal = document.getElementById('deleteModal')
if (deleteModal) {
  deleteModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget;
    // Extract info from data-bs-* attributes
    let recipient = button.getAttribute('data-bs-deletable-object');
    // If necessary, you could initiate an Ajax request here
    // and then do the updating in a callback.

    // If no single object is specified, get all selected checkboxes
    if (!recipient) {
      const checkedBoxes = document.querySelectorAll('input[name="selected_objects"]:checked');
      recipient = Array.from(checkedBoxes).map(checkbox => checkbox.value).join(', ');
    }

    // Update the modal's content.
    const modalTitle = deleteModal.querySelector('.deletable-object-title');
    const deleteModalBody = deleteModal.querySelector('#deleteModalBody');

    modalTitle.textContent = `${recipient}`;
    deleteModalBody.value = recipient;
  });
}

// Toggle delete button visibility based on checkbox selection
function toggleDeleteButton() {
  const checkedBoxes = document.querySelectorAll('input[name="selected_objects"]:checked');
  const deleteBtn = document.getElementById('list-delete-btn');
  deleteBtn.style.display = checkedBoxes.length > 0 ? 'inline-block' : 'none';
}

function toggleSelectAll(state) {
  const checkboxes = document.querySelectorAll('input[name="selected_objects"]');
  checkboxes.forEach(checkbox => {
    checkbox.checked = state;
  });
  toggleDeleteButton();
}

// Add event listeners to all checkboxes
document.querySelectorAll('input[name="selected_objects"]').forEach(checkbox => {
  checkbox.addEventListener('change', toggleDeleteButton);
});

// Add event listener to the "select all" checkbox
const selectAllCheckbox = document.getElementById('select-all');
if (selectAllCheckbox) {
  selectAllCheckbox.addEventListener('change', function() {
    toggleSelectAll(this.checked);
  });
}
