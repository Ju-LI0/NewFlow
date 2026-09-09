document.addEventListener("DOMContentLoaded", function () {

    const musicInterface = document.querySelector(".music-interface");

    if (!musicInterface) {
        console.log("NewFlow: .music-interface não encontrada.");
        return;
    }

    console.log("NewFlow: interação do card carregada.");

    const maxRotation = 7;

    musicInterface.addEventListener("mouseenter", function () {

        musicInterface.style.transition =
            "transform 0.15s ease-out, box-shadow 0.25s ease";

        musicInterface.style.boxShadow =
            "0 40px 100px rgba(0, 0, 0, 0.6), 0 0 45px rgba(30, 215, 96, 0.18)";

        musicInterface.style.cursor = "default";
    });


    musicInterface.addEventListener("mousemove", function (event) {

        const rect = musicInterface.getBoundingClientRect();

        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateY =
            ((x - centerX) / centerX) * maxRotation;

        const rotateX =
            ((centerY - y) / centerY) * maxRotation;

        musicInterface.style.transform = `
            perspective(1000px)
            rotateY(${rotateY}deg)
            rotateX(${rotateX}deg)
            translateY(-5px)
            scale(1.015)
        `;
    });


    musicInterface.addEventListener("mouseleave", function () {

        musicInterface.style.transition =
            "transform 0.5s ease, box-shadow 0.5s ease";

        musicInterface.style.transform = `
            perspective(1000px)
            rotateY(-7deg)
            rotateX(3deg)
            translateY(0)
            scale(1)
        `;

        musicInterface.style.boxShadow =
            "0 40px 100px rgba(0, 0, 0, 0.5)";
    });

});