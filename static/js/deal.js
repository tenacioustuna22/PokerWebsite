function cardPath(rankSuitArr) {
    return `/static/images/cards/${rankSuitArr[0]}${rankSuitArr[1]}.png`;
  }
  
  // update the two <img> tags that already exist in the HTML
  function updateCards(hands) {
    Object.entries(hands).forEach(([playerId, hand]) => {
      const img1 = document.querySelector(`#p${playerId}-card1`);
      const img2 = document.querySelector(`#p${playerId}-card2`);
      if (img1 && img2) {
        img1.src = cardPath(hand[0]);
        img2.src = cardPath(hand[1]);
      }
    });
  }

  function updateCards(hands) {
    Object.entries(hands).forEach(([playerId, hand]) => {
      const img3 = document.querySelector(`#p${playerId}-card3`);
      const img4 = document.querySelector(`#p${playerId}-card4`);
      if (img3 && img4) {
        img3.src = cardPath(hand[0]);
        img4.src = cardPath(hand[1]);
      }
    });
  }
  
  // one-time wiring for the Start button
  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("start-btn");
    if (!btn) return;
  
    btn.addEventListener("click", async () => {
      const url   = btn.dataset.url;
      const token = btn.dataset.csrftoken;
  
      const res = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": token }
      });
  
      if (!res.ok) {
        alert("Server error " + res.status);
        return;
      }
  
      const data = await res.json();   // {hands: {12:[["A","S"],["K","C"]], …}}
      updateCards(data.hands);
    });
  });
