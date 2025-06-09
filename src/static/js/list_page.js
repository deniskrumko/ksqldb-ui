function updateStreamFilters() {
  const activeFilters = Array.from(document.querySelectorAll('.filter-item.active')).map(el => el.textContent.trim());
  const rows = document.querySelectorAll('.list-view-row');

  if (activeFilters.length === 0) {
    rows.forEach(row => {
      row.style.display = '';
    });
    return;
  }

  rows.forEach(row => {
    const normalize = s => s.toLowerCase().replace(/[\s-]/g, '_');
    const filterNames = normalize(row.getAttribute('data-filter-name') || '');
    const normalizedActiveFilters = activeFilters.map(f => normalize(f));
    const hasAllFilters = normalizedActiveFilters.every(f => filterNames.includes(f));
    row.style.display = hasAllFilters ? '' : 'none';
  });

  console.log('Active filters:', activeFilters);
}


document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".filter-item").forEach(function (item) {
    item.addEventListener("click", function () {
      this.classList.toggle("active");
      updateStreamFilters();
    });
  });

  document.getElementById("filter-reset").addEventListener("click", function () {
    document.querySelectorAll(".filter-item").forEach(function (item) {
      item.classList.remove("active");
    });

    activeFilters = [];
    updateStreamFilters();
  })
});
