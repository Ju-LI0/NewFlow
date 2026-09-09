document.addEventListener(
    "DOMContentLoaded",
    function () {

        const generateButtons = document.querySelectorAll(
            ".generate-button"
        );


        generateButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        if (
                            button.classList.contains(
                                "loading"
                            )
                        ) {

                            return;

                        }


                        button.classList.add(
                            "loading"
                        );


                        button.setAttribute(
                            "aria-disabled",
                            "true"
                        );


                        button.style.pointerEvents =
                            "none";


                        const buttonText =
                            button.querySelector(
                                ".button-text"
                            );


                        const buttonIcon =
                            button.querySelector(
                                ".button-icon"
                            );


                        if (buttonText) {

                            buttonText.textContent =
                                "Gerando recomendações...";

                        }


                        if (buttonIcon) {

                            buttonIcon.textContent =
                                "⏳";

                        }

                    }
                );

            }
        );


        const flashMessages =
            document.querySelectorAll(
                ".flash-message"
            );


        flashMessages.forEach(
            function (message) {

                setTimeout(
                    function () {

                        message.classList.add(
                            "hide"
                        );

                    },
                    5000
                );

            }
        );

    }
);