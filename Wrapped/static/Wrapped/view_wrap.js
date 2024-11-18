const numberOfSlides = 5;
let currentSlide = 0;

let progressTimeout = null;
const progressBar = document.getElementById("progress-bar")

const startProgressAnimation = (nextSlideIndex) => {
    progressBar.classList.remove("active");
    progressBar.offsetHeight
    progressBar.classList.add("active");
    progressTimeout = setTimeout(() => {
        selectSlide(nextSlideIndex);
        if (nextSlideIndex < numberOfSlides - 1) {
            startProgressAnimation(nextSlideIndex + 1);
        }
    }, 10 * 1000)
}

const selectSlide = (slideIndex) => {
    for (let slide of document.getElementsByClassName("wrap-slide")){
        slide.style.display = "none";
    }
    let slideElement = document.getElementById(`wrap-slide-${slideIndex}`);
    slideElement.style.display = "block";
    for (let button of document.getElementsByClassName("pagination")[0].children){
        button.classList.remove("active");
    }
    let activeButtonElement = document.getElementById(`slide-button-${slideIndex}`);
    activeButtonElement.classList.add("active");
    currentSlide = slideIndex;
}

selectSlide(0);
startProgressAnimation(1);

for (let i = 0; i < numberOfSlides; i++) {
    document.getElementById(`slide-button-${i}`).addEventListener("click", () => {
        clearTimeout(progressTimeout)
        progressBar.classList.remove("active");
        progressBar.offsetHeight;
        selectSlide(i);
    })
}

document.getElementById("slide-back-button").addEventListener("click", () => {
    if (currentSlide > 0) {
        selectSlide(currentSlide - 1)
    }
})

document.getElementById("slide-forward-button").addEventListener("click", () => {
    if (currentSlide < numberOfSlides - 1) {
        selectSlide(currentSlide + 1)
    }
})