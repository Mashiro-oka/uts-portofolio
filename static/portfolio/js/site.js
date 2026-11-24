const upload = document.querySelector("[data-image-upload]");
const preview = document.querySelector("[data-image-preview]");

if (upload && preview) {
  const existingImage = preview.querySelector("img");
  const image = existingImage || new Image();
  image.className = "preview";
  image.alt = "Pratinjau gambar proyek";
  const existingSource = existingImage?.src;
  let previewUrl;

  upload.addEventListener("change", () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = undefined;
    }
    const file = upload.files[0];
    if (
      file &&
      ["image/jpeg", "image/png", "image/webp"].includes(file.type) &&
      file.size <= 2 * 1024 * 1024
    ) {
      previewUrl = URL.createObjectURL(file);
    }
    const source = previewUrl || existingSource;
    if (source) {
      image.src = source;
      if (!image.isConnected) preview.append(image);
    } else {
      image.remove();
      image.removeAttribute("src");
    }
  });
}

const menuToggle = document.querySelector(".menu-toggle");

if (menuToggle) {
  const navigation = document.getElementById(menuToggle.getAttribute("aria-controls"));

  let touchStartY;

  function setMenuOpen(open) {
    menuToggle.setAttribute("aria-expanded", String(open));
  }

  function closeMobileMenu() {
    if (
      menuToggle.getAttribute("aria-expanded") !== "true" ||
      !menuToggle.getClientRects().length
    ) return;

    const focusWasInMenu = navigation.contains(document.activeElement);
    setMenuOpen(false);
    if (focusWasInMenu) menuToggle.focus({ preventScroll: true });
  }

  window.addEventListener("scroll", closeMobileMenu, { capture: true, passive: true });
  window.addEventListener("wheel", (event) => {
    if (event.deltaY && !event.ctrlKey) closeMobileMenu();
  }, { passive: true });
  window.addEventListener("touchstart", (event) => {
    touchStartY = event.touches.length === 1 ? event.touches[0].clientY : undefined;
  }, { passive: true });
  window.addEventListener("touchmove", (event) => {
    if (touchStartY !== undefined && event.touches.length === 1 &&
        Math.abs(event.touches[0].clientY - touchStartY) >= 6) {
      closeMobileMenu();
    }
  }, { passive: true });

  menuToggle.addEventListener("click", () => {
    setMenuOpen(menuToggle.getAttribute("aria-expanded") === "false");
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenuOpen(false);
  });

  menuToggle.closest("header").addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMobileMenu();
  });

  menuToggle.hidden = false;
}
