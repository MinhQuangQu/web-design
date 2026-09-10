const form = document.querySelector('#prediction-form');
const button = document.querySelector('#submit-button');
const result = document.querySelector('#result');
const price = document.querySelector('#price');
const resultDetail = document.querySelector('#result-detail');
const errorMessage = document.querySelector('#error-message');
const moneyFormatter = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 });

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorMessage.classList.remove('visible');
  result.classList.remove('visible');
  button.disabled = true;
  button.textContent = 'Đang tính toán...';

  const params = new URLSearchParams({
    area: document.querySelector('#area').value,
    bedrooms: document.querySelector('#bedrooms').value,
    location: document.querySelector('#location').value
  });

  try {
    // Relative URL works because the frontend and API share the same origin.
    const response = await fetch(`/predict?${params.toString()}`);
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    const data = await response.json();

    price.textContent = moneyFormatter.format(data.predicted_price);
    resultDetail.textContent = `${data.area} m² · ${data.bedrooms} phòng ngủ · ${data.location}`;
    result.classList.add('visible');
  } catch (error) {
    errorMessage.textContent = 'Không thể lấy kết quả lúc này. Hãy kiểm tra API và thử lại.';
    errorMessage.classList.add('visible');
  } finally {
    button.disabled = false;
    button.textContent = 'Ước tính giá nhà';
  }
});
