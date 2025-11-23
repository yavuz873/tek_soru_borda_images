// ==========================
//   TIKLAMALI SIRALAMA (FINAL)
// ==========================

let order = [];
let maxCount = 0;

document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card");
  maxCount = cards.length;

  cards.forEach(card => {
    const name = card.dataset.name?.trim();
    if (!name) return;

    card.addEventListener("click", () => selectCandidate(name, card));
  });

  updateUI();
});

// ✔ Kart Seçme - Görsel efekt + liste
function selectCandidate(name, card) {

  if (order.includes(name)) {
    order = order.filter(n => n !== name);
    card.classList.remove("selected");
  }
  else if (order.length < maxCount) {
    order.push(name);
    card.classList.add("selected");
  }

  updateUI();
}

// ✔ Görsel güncelleme
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

// ✔ Kaydet
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
    .then(res => res.ok ? window.location.href = "/results" : alert(res.msg));
});
function removeCandidate(name, event) {
  event.stopPropagation(); // kart tıklamasını engelle
  order = order.filter(n => n !== name);
  updateUI();
}
// ↩️ Tek tuşla tümünü sıfırla
document.getElementById("resetBtn")?.addEventListener("click", () => {
  order = [];  // sıralamayı boşalt
  document.querySelectorAll(".card").forEach(c => c.classList.remove("selected"));
  updateUI();
});
