const dynamicText = document.querySelector("h1 span");
const kata = ["Keindahan Alam", "Keragaman Budaya", "Destinasi Menarik", "Semuanya!"];

let indexKata = 0;
let indexHuruf = 0;
let hapus = false;

const typeEffect = () => {
  const kataAwal = kata[indexKata];
  const hurufAwal = kataAwal.substring(0, indexHuruf);
  dynamicText.textContent = hurufAwal;
  dynamicText.classList.add("stop-blinking");

  if (!hapus && indexHuruf < kataAwal.length) {
    indexHuruf++;
    setTimeout(typeEffect, 200);
  } else if (hapus && indexHuruf > 0) {
    indexHuruf--;
    setTimeout(typeEffect, 100);
  } else {
    hapus = !hapus;
    dynamicText.classList.remove("stop-blinking");
    indexKata = !hapus ? (indexKata + 1) % kata.length : indexKata;
    setTimeout(typeEffect, 1200);
  }
};

typeEffect();
