const map = L.map('map', { zoomControl: false }).setView([48.8566, 2.3522], 5);
L.control.zoom({ position: 'bottomright' }).addTo(map);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }).addTo(map);

let token = localStorage.getItem('spotapp_token');
let selectedLocation = null;
let markers = [];
let filter = 'all';
const user = { user_id: 1, disabled: false };
const $ = (id) => document.getElementById(id);

function setMessage(id, message, error = true) {
  $(id).textContent = message;
  $(id).style.color = error ? 'var(--orange)' : 'var(--teal)';
}
function markerIcon(type) {
  return L.divIcon({ className: '', html: `<div class="spot-marker ${type}"></div>`, iconSize: [17, 17], iconAnchor: [8, 8], popupAnchor: [0, -8] });
}
function drawSpots(spots) {
  markers.forEach((marker) => map.removeLayer(marker));
  markers = spots.filter((spot) => filter === 'all' || spot.sport_type === filter).map((spot) => {
    const marker = L.marker([spot.latitude, spot.longitude], { icon: markerIcon(spot.sport_type) }).addTo(map);
    marker.bindPopup(`<div class="popup-title">${spot.spot_name}</div><div class="popup-meta">${spot.sport_type} · ${spot.spot_description || 'Community spot'}</div>`);
    return marker;
  });
  $('map-note').textContent = `${markers.length} spot${markers.length === 1 ? '' : 's'} nearby`;
}
async function loadSpots() {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch('/spots/filtered/', { headers });
  if (!response.ok) { $('map-note').textContent = 'Could not load spots.'; return; }
  drawSpots(await response.json());
}
function setLoggedIn(email) {
  $('auth-panel').classList.add('hidden');
  $('user-panel').classList.remove('hidden');
  $('spot-panel').classList.remove('hidden');
  $('user-email').textContent = email;
  $('user-avatar').textContent = email[0].toUpperCase();
  loadSpots();
}
async function authSubmit(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  const register = event.target.dataset.mode === 'register';
  if (register) {
    const response = await fetch('/users/create/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nickname: data.nickname, first_name: data.nickname, last_name: data.nickname, user_pic: null, email: data.email, password: data.password }) });
    if (!response.ok) { setMessage('auth-message', 'Registration failed. Check your details.'); return; }
  }
  const body = new URLSearchParams({ username: data.email, password: data.password });
  const response = await fetch('/login', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
  if (!response.ok) { setMessage('auth-message', 'Incorrect email or password.'); return; }
  const result = await response.json();
  token = result.access_token;
  localStorage.setItem('spotapp_token', token);
  setLoggedIn(data.email);
}
async function publishSpot(event) {
  event.preventDefault();
  if (!selectedLocation) { setMessage('spot-message', 'Choose a point on the map first.'); return; }
  const data = Object.fromEntries(new FormData(event.target));
  const response = await fetch('/spots/create/', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ ...data, spot_pic: null, spot_photos: [], spot_country: 'Unknown', spot_city: 'Unknown', spot_street: 'Map point', spot_street_number: '0', comment: [], latitude: selectedLocation.lat, longitude: selectedLocation.lng }) });
  if (!response.ok) { setMessage('spot-message', 'Could not publish this spot.'); return; }
  setMessage('spot-message', 'Spot published.', false);
  event.target.reset();
  loadSpots();
}
$('auth-form').addEventListener('submit', authSubmit);
$('spot-form').addEventListener('submit', publishSpot);
document.querySelectorAll('.tab').forEach((tab) => tab.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach((item) => item.classList.remove('active'));
  tab.classList.add('active');
  const register = tab.dataset.mode === 'register';
  $('auth-form').dataset.mode = tab.dataset.mode;
  $('name-field').classList.toggle('hidden', !register);
  $('auth-submit').textContent = register ? 'Create account' : 'Log in';
}));
document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.filter').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  filter = button.dataset.filter;
  loadSpots();
}));
map.on('click', (event) => {
  selectedLocation = event.latlng;
  $('latitude').textContent = event.latlng.lat.toFixed(5);
  $('longitude').textContent = event.latlng.lng.toFixed(5);
  L.popup().setLatLng(event.latlng).setContent('New spot location').openOn(map);
});
$('locate').addEventListener('click', () => navigator.geolocation.getCurrentPosition((position) => map.setView([position.coords.latitude, position.coords.longitude], 13)));
$('logout').addEventListener('click', () => { localStorage.removeItem('spotapp_token'); location.reload(); });
$('search-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = $('search-input').value.trim();
  if (!query) return;
  const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query)}`, { headers: { Accept: 'application/json' } });
  const result = (await response.json())[0];
  if (result) map.setView([result.lat, result.lon], 13);
});
loadSpots();
if (token) setLoggedIn('returning rider');
