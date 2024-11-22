const numberOfSlides = 5;
let currentSlide = 0;

let progressTimeout = null;
const progressBar = document.getElementById("progress-bar")

let fadeInterval = null;
const animationTime = 10 * 1000;

const startProgressAnimation = (nextSlideIndex) => {
    progressBar.classList.remove("active");
    progressBar.offsetHeight
    progressBar.classList.add("active");
    clearTimeout(progressTimeout)
    progressTimeout = setTimeout(() => {
        selectSlide(nextSlideIndex, true);
    }, animationTime)
}

const fadeVolume = (audioElement, startVolume, endVolume, duration) => {
    console.log("Fading start");
    let startTime = Date.now();
    if (fadeInterval) clearInterval(fadeInterval);
    fadeInterval = setInterval(() => {
        let elapsedTime = Date.now() - startTime;
        let progress = Math.min(elapsedTime / duration, 1);
        audioElement.volume = startVolume + (Math.log10(progress + 1) / Math.log10(2)) * (endVolume - startVolume);

        if (progress === 1) {
            clearInterval(fadeInterval);
            console.log("Fading end");
        }
    }, 50);
};

const selectSlide = (slideIndex, animate) => {
    const audioPlayer = document.getElementById("audio-player");
    let fadeOutDuration = 2500;
    let playDuration = 30000 - fadeOutDuration;
    audioPlayer.pause();
    audioPlayer.volume = 0;
    audioPlayer.src = "";

    if(animate){
        playDuration = animationTime - fadeOutDuration;
        if (slideIndex < numberOfSlides - 1) {
            startProgressAnimation(slideIndex+1)
        }
    } else if (progressBar.classList.contains("active")) {
        progressBar.classList.remove("active");
        progressBar.offsetHeight
    }
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

    audioPlayer.src = slideElement.dataset.previewUrl;
    audioPlayer.play()
    fadeVolume(audioPlayer, 0, 0.125, 3000);
    setTimeout(() => {
        fadeVolume(audioPlayer, audioPlayer.volume, 0, fadeOutDuration);
    }, playDuration - 100);

    currentSlide = slideIndex;
}

selectSlide(0, true);

for (let i = 0; i < numberOfSlides; i++) {
    document.getElementById(`slide-button-${i}`).addEventListener("click", () => {
        clearTimeout(progressTimeout)
        progressBar.classList.remove("active");
        progressBar.offsetHeight;
        selectSlide(i, false);
    })
}

document.getElementById("slide-back-button").addEventListener("click", () => {
    if (currentSlide > 0) {
        selectSlide(currentSlide - 1, true)
    }
})

document.getElementById("slide-forward-button").addEventListener("click", () => {
    if (currentSlide < numberOfSlides - 1) {
        selectSlide(currentSlide + 1, true)
    }
})

const emojis = ["https://em-content.zobj.net/source/apple/391/grinning-face-with-big-eyes_1f603.png", "https://em-content.zobj.net/source/apple/391/guitar_1f3b8.png", "https://em-content.zobj.net/source/apple/391/woman-dancing_1f483.png"];

const temp = document.getElementById("emojiTemplate").content.querySelector("img");
const emojiContainer = document.getElementById("emojiContainer");

for (let i = 0; i < 150; i++) {
    let clone = temp.cloneNode(true);
    clone.src = emojis[Math.floor(Math.random() * emojis.length)]
    clone.style.top = Math.floor(Math.random() * 90) + 5 + "%"
    clone.style.left = Math.floor(Math.random() * 90) + 5 + "%"
    emojiContainer.appendChild(clone);
}
