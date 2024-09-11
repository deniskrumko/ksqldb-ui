const deleteModal = document.getElementById('deleteModal')
if (deleteModal) {
  deleteModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const recipient = button.getAttribute('data-bs-deletable-object')
    // If necessary, you could initiate an Ajax request here
    // and then do the updating in a callback.

    // Update the modal's content.
    const modalTitle = deleteModal.querySelector('.deletable-object-title')
    const deleteModalBody = deleteModal.querySelector('#deleteModalBody')

    modalTitle.textContent = `${recipient}`
    deleteModalBody.value = recipient
  })
}
