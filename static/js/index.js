let order = [];  // seçilen sıralama
const maxCount = 6; // aday sayısı

function selectCandidate(name) {

  // Eğer zaten seçiliyse → kaldır
  if (order.includes(name)) {
    order = order.filter(n => n !== name);
  }
  // Değilse sıraya ekle (max sınır)
  else if (order.length < maxCount) {
    order.push(name);
  }

  updateUI();
}

function updateUI() {

  // Tüm badge’leri sıfırla
  document.querySelectorAll('.rank-badge').forEach(badge => {
    badge.textContent = "–";
    badge.style.background = "#5a422e";
  });

  // Seçilenlere numara koy
  order.forEach((name, index) => {
    const badge = document.getElementById("badge-" + name);
    badge.textContent = (index + 1);
    badge.style.background = "#7c5a3d";
  });

  // Listeyi güncelle
  const list = document.getElementById("orderList");
  list.innerHTML = "";
  order.forEach(n => {
    const li = document.createElement("li");
    li.textContent = n;
    list.appendChild(li);
  });
}

// Kaydet
document.getElementById("saveBtn").onclick = () => {

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
};
