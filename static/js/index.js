// ==========================
//   TIKLAMALI SIRALAMA
// ==========================

let order = [];
let maxCount = 6;

// Sayfa açılınca kartlara tıklama ekle
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card");

  maxCount = cards.length; // otomatik aday sayısı

  cards.forEach(card => {
    const name = card.dataset.name;
    if (!name) return;

    card.addEventListener("click", () => selectCandidate(name));
  });

  updateUI();
});

// Kart seçme – eski kodun birebir aynısı
function selectCandidate(name) {

  if (order.includes(name)) {
    order = order.filter(n => n !== name);
  }
  else if (order.length < maxCount) {
    order.push(name);
  }

  updateUI();
}

// UI güncelleme – eski kod aynen duruyor
function updateUI() {

  document.querySelectorAll('.rank-badge').forEach(badge => {
    badge.textContent = "–";
    badge.style.background = "#5a422e";
  });

  order.forEach((name, index) => {
    const badge = document.getElementById("badge-" + name);
    badge.textContent = (index + 1);
    badge.style.background = "#7c5a3d";
  });

  const list = document.getElementById("orderList");
  if (list) {
    list.innerHTML = "";
    order.forEach(n => {
      const li = document.createElement("li");
      li.textContent = n;
      list.appendChild(li);
    });
  }
}

// Kaydet – eski kodun aynısı
document.getElementById("saveBtn")?.addEventListener("click", () => {

  if (order.length !== maxCount) {
    alert("Lütfen tüm adayları sıralayın.");
    return;
  }

  fetch("/vote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order })
  })
  .then(r => r.json())
  .then(res => {
    if (res.ok) {
      window.location.href = "/results";
    } else {
      alert(res.msg);
    }
  });
});
