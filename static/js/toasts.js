document.addEventListener(
    "DOMContentLoaded",
    () => {

        const flashMessages =
            document.querySelectorAll(
                ".flash-message"
            );

        flashMessages.forEach(
            (message, index) => {

                setTimeout(() => {

                    message.classList.add(
                        "flash-hide"
                    );

                    setTimeout(() => {

                        message.remove();

                    }, 350);

                }, 3500 + (index * 200));

            }
        );

    }
);