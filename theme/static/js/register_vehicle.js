function preview(input, previewId, textId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      document.getElementById(previewId).innerHTML =
        `<img src="${e.target.result}">`;

      const text = document.getElementById(textId);

      text.innerHTML = "✔ " + input.files[0].name;

      text.classList.add("upload-success");
    };

    reader.readAsDataURL(input.files[0]);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const uploads = [
    ["vehicle_front_image", "frontPreview", "frontText"],

    ["vehicle_back_image", "backPreview", "backText"],

    ["number_plate_image", "platePreview", "plateText"],

    ["bluebook_image", "bluebookPreview", "bluebookText"],
  ];

  uploads.forEach((item) => {
    const input = document.querySelector(`[name='${item[0]}']`);

    if (input) {
      input.onchange = () => {
        preview(input, item[1], item[2]);
      };
    }
  });

  document.querySelectorAll(".upload-box").forEach((box) => {
    box.addEventListener("dragover", (e) => {
      e.preventDefault();

      box.style.borderColor = "#dc2626";

      box.style.background = "rgba(220,38,38,.08)";
    });

    box.addEventListener("dragleave", () => {
      box.style.borderColor = "";

      box.style.background = "";
    });
  });
});
