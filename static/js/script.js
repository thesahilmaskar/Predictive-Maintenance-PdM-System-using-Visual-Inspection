// Crack Detection
const crackForm = document.getElementById('crackForm');
const imageInput = document.getElementById('imageInput');
const crackResult = document.getElementById('crackResult');
const crackAlert = document.getElementById('crackAlert');

crackForm.addEventListener('submit', async (e) => {
  e.preventDefault(); crackAlert.innerHTML = ''; crackResult.style.display = 'none';
  if (!imageInput.files.length) { crackAlert.innerHTML = '<div class="alert alert-warning">Select an image.</div>'; return; }
  const formData = new FormData(); formData.append('image', imageInput.files[0]);
  try {
    const res = await fetch('/detect', { method: 'POST', body: formData });
    if (!res.ok) {
      const err = await res.json(); throw new Error(err.error || 'Detection error');
    }
    const blob = await res.blob(); crackResult.src = URL.createObjectURL(blob);
    crackResult.style.display = 'block';
  } catch (err) {
    crackAlert.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
});

// Feature-Based Prediction
const featureForm = document.getElementById('featureForm');
const featureResult = document.getElementById('featureResult');

featureForm.addEventListener('submit', async (e) => {
  e.preventDefault(); featureResult.textContent = '';
  const features = [
    parseFloat(document.getElementById('f1').value),
    parseFloat(document.getElementById('f2').value),
    parseFloat(document.getElementById('f3').value),
    parseFloat(document.getElementById('f4').value),
    isNaN(document.getElementById('f5').value) ? document.getElementById('f5').value : document.getElementById('f5').value
  ];
  try {
    const res = await fetch('/predict', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ features })
    });
    const data = await res.json();
    if (data.prediction !== undefined) {
      featureResult.innerHTML = `Prediction: ${data.prediction}`;
    } else {
      throw new Error(data.error);
    }
  } catch (err) {
    featureResult.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
});

// .mat Signal Fault Detection
const matForm = document.getElementById('matForm');
const matInput = document.getElementById('matInput');
const matResult = document.getElementById('matResult');

matForm.addEventListener('submit', async (e) => {
  e.preventDefault(); matResult.textContent = '';
  if (!matInput.files.length) { matResult.innerHTML = '<div class="alert alert-warning">Select a .mat file.</div>'; return; }
  const formData = new FormData(); formData.append('file', matInput.files[0]);
  try {
    const res = await fetch('/fault_detect', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.result) {
      matResult.innerHTML = `<h2>${data.result}</h2>`;
    } else {
      throw new Error(data.error);
    }
  } catch (err) {
    matResult.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
});