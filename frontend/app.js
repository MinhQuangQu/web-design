const form = document.querySelector('#item-form');
const itemIdInput = document.querySelector('#item-id');
const nameInput = document.querySelector('#name');
const priceInput = document.querySelector('#price');
const inStockInput = document.querySelector('#in-stock');
const submitButton = document.querySelector('#submit-button');
const cancelButton = document.querySelector('#cancel-button');
const filtersForm = document.querySelector('#filters-form');
const itemsList = document.querySelector('#items-list');
const message = document.querySelector('#message');
const paginationInfo = document.querySelector('#pagination-info');
const previousButton = document.querySelector('#previous-page');
const nextButton = document.querySelector('#next-page');
const predictionForm = document.querySelector('#prediction-form');
const predictionResult = document.querySelector('#prediction-result');

let currentSkip = 0;
let currentLimit = 10;
let currentTotal = 0;

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers
    }
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail) || `Request failed (${response.status})`);
  }
  return data;
}

function showMessage(text, isError = false) {
  message.textContent = text;
  message.dataset.error = String(isError);
}

function resetForm() {
  form.reset();
  itemIdInput.value = '';
  submitButton.textContent = 'Create item';
  cancelButton.hidden = true;
}

function beginEdit(item) {
  itemIdInput.value = item.id;
  nameInput.value = item.name;
  priceInput.value = item.price;
  inStockInput.checked = item.in_stock;
  submitButton.textContent = 'Save changes (PATCH)';
  cancelButton.hidden = false;
  nameInput.focus();
}

function renderItems(items) {
  itemsList.replaceChildren();

  if (items.length === 0) {
    const empty = document.createElement('li');
    empty.textContent = 'No matching items.';
    itemsList.append(empty);
    return;
  }

  for (const item of items) {
    const row = document.createElement('li');
    const details = document.createElement('span');
    details.textContent = `#${item.id} ${item.name} — ${item.price} — ${item.in_stock ? 'In stock' : 'Out of stock'}`;

    const viewButton = document.createElement('button');
    viewButton.type = 'button';
    viewButton.textContent = 'View';
    viewButton.addEventListener('click', () => loadItem(item.id));

    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.textContent = 'Edit';
    editButton.addEventListener('click', () => beginEdit(item));

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', () => deleteItem(item.id));

    row.append(details, ' ', viewButton, ' ', editButton, ' ', deleteButton);
    itemsList.append(row);
  }
}

async function loadItems() {
  const params = new URLSearchParams({
    skip: String(currentSkip),
    limit: String(currentLimit),
    sort_by: filtersForm.elements.sort_by.value,
    order: filtersForm.elements.order.value
  });

  for (const key of ['min_price', 'max_price', 'q']) {
    const value = filtersForm.elements[key].value.trim();
    if (value) params.set(key, value);
  }

  try {
    const result = await apiRequest(`/items?${params.toString()}`);
    currentTotal = result.total;
    renderItems(result.items);
    paginationInfo.textContent = `Showing ${result.items.length} of ${result.total} matching item(s).`;
    previousButton.disabled = currentSkip === 0;
    nextButton.disabled = currentSkip + currentLimit >= currentTotal;
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function loadItem(id) {
  try {
    const item = await apiRequest(`/items/${id}`);
    showMessage(`Item #${item.id}: ${item.name}, price ${item.price}, ${item.in_stock ? 'in stock' : 'out of stock'}`);
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function deleteItem(id) {
  try {
    const result = await apiRequest(`/items/${id}`, { method: 'DELETE' });
    showMessage(result.message);
    if (itemIdInput.value === String(id)) resetForm();
    if (currentSkip > 0 && currentSkip >= currentTotal - 1) {
      currentSkip = Math.max(0, currentSkip - currentLimit);
    }
    await loadItems();
  } catch (error) {
    showMessage(error.message, true);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const itemId = itemIdInput.value;
  const item = {
    name: nameInput.value.trim(),
    price: Number(priceInput.value),
    in_stock: inStockInput.checked
  };

  submitButton.disabled = true;
  try {
    const savedItem = await apiRequest(itemId ? `/items/${itemId}` : '/items', {
      method: itemId ? 'PATCH' : 'POST',
      body: JSON.stringify(item)
    });
    showMessage(itemId ? `Updated item #${savedItem.id}.` : `Created item #${savedItem.id}.`);
    resetForm();
    await loadItems();
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

filtersForm.addEventListener('submit', (event) => {
  event.preventDefault();
  currentLimit = Math.max(1, Number(filtersForm.elements.limit.value) || 10);
  currentSkip = 0;
  loadItems();
});

document.querySelector('#clear-filters').addEventListener('click', () => {
  filtersForm.reset();
  filtersForm.elements.limit.value = '10';
  currentSkip = 0;
  currentLimit = 10;
  loadItems();
});

previousButton.addEventListener('click', () => {
  currentSkip = Math.max(0, currentSkip - currentLimit);
  loadItems();
});

nextButton.addEventListener('click', () => {
  if (currentSkip + currentLimit < currentTotal) {
    currentSkip += currentLimit;
    loadItems();
  }
});

predictionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  predictionResult.textContent = 'Predicting...';
  const request = {
    area_sqm: Number(predictionForm.elements.area_sqm.value),
    bedrooms: Number(predictionForm.elements.bedrooms.value),
    distance_to_center_km: Number(predictionForm.elements.distance_to_center_km.value)
  };

  try {
    const result = await apiRequest('/predict/house-price', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    predictionResult.textContent = `Predicted price: ${new Intl.NumberFormat('vi-VN').format(result.predicted_price)} ${result.currency}`;
  } catch (error) {
    predictionResult.textContent = error.message;
  }
});

cancelButton.addEventListener('click', resetForm);
loadItems();
