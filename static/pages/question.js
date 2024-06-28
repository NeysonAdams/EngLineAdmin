const questionButtons = document.querySelectorAll(".questions__dropdown");
const questionIcons = document.querySelectorAll(".questions__dropdown-icon");
const questionAnswers = document.querySelectorAll(
  ".questions__dropdown-answer"
);
let picked = -1;

function closeAllAnswers() {
  questionButtons.forEach((item) => {
    item.classList.remove("questions__dropdown-picked");
  });
  questionIcons.forEach((item) => {
    item.classList.remove("questions__dropdown-icon-picked");
  });
  questionAnswers.forEach((item) => {
    item.classList.remove("questions__dropdown-answer-opened");
  });
}

const handleDropdown = (event) => {
  closeAllAnswers();
  if (picked == event.currentTarget.id) {
    picked = -1;
    return;
  }
  picked = event.currentTarget.id;
  event.currentTarget.classList.add("questions__dropdown-picked");
  questionIcons[picked].classList.add("questions__dropdown-icon-picked");
  questionAnswers[picked].classList.add("questions__dropdown-answer-opened");
};

questionButtons.forEach((button) => {
  button.addEventListener("click", handleDropdown);
});
