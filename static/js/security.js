document.addEventListener(
    "DOMContentLoaded",
    () => {

        /*
        =========================================
        PASSWORD VISIBILITY TOGGLE
        =========================================
        */

        const passwordFields =
            document.querySelectorAll(
                'input[type="password"]'
            );

        passwordFields.forEach(
            (input) => {

                const wrapper =
                    document.createElement("div");

                wrapper.className =
                    "password-field-wrapper";

                input.parentNode.insertBefore(
                    wrapper,
                    input
                );

                wrapper.appendChild(input);

                const toggle =
                    document.createElement("button");

                toggle.type = "button";

                toggle.className =
                    "password-toggle-btn";

                toggle.innerHTML = `
                    <i data-lucide="eye"></i>
                `;

                wrapper.appendChild(toggle);

                toggle.addEventListener(
                    "click",
                    () => {

                        const isPassword =
                            input.type === "password";

                        input.type =
                            isPassword
                            ? "text"
                            : "password";

                        toggle.innerHTML =
                            isPassword
                            ? '<i data-lucide="eye-off"></i>'
                            : '<i data-lucide="eye"></i>';

                        if(window.lucide){

                            lucide.createIcons();

                        }

                    }
                );

            }
        );

        /*
        =========================================
        DISABLE COPY / PASTE
        =========================================
        */

        const secureFields =
            document.querySelectorAll(
                'input[type="password"]'
            );

        secureFields.forEach(
            (field) => {

                [
                    "copy",
                    "paste",
                    "cut",
                    "drag",
                    "drop"
                ].forEach(
                    (eventType) => {

                        field.addEventListener(
                            eventType,
                            (event) => {

                                event.preventDefault();

                            }
                        );

                    }
                );

                /*
                =========================================
                AUTOCOMPLETE SECURITY
                =========================================
                */

                field.setAttribute(
                    "autocomplete",
                    "new-password"
                );

                field.setAttribute(
                    "spellcheck",
                    "false"
                );

                field.setAttribute(
                    "autocapitalize",
                    "off"
                );

                field.setAttribute(
                    "autocorrect",
                    "off"
                );

            }
        );

        /*
        =========================================
        FORCE REMOVE AUTOFILL
        =========================================
        */

        setTimeout(() => {

            document
            .querySelectorAll("input")
            .forEach((input) => {

                input.value =
                    input.value;

            });

        }, 100);

        /*
        =========================================
        RELOAD ICONS
        =========================================
        */

        if(window.lucide){

            lucide.createIcons();

        }

    }
);


/*
=========================================
DOB AUTO FORMAT
=========================================
*/

const dobInput =
    document.getElementById(
        "date_of_birth"
    );

if(dobInput){

    dobInput.addEventListener(
        "input",
        (event) => {

            let value =
                event.target.value
                .replace(/\D/g, "")
                .slice(0, 8);

            if(value.length > 4){

                value =
                    value.replace(
                        /(\d{2})(\d{2})(\d+)/,
                        "$1/$2/$3"
                    );

            }

            else if(value.length > 2){

                value =
                    value.replace(
                        /(\d{2})(\d+)/,
                        "$1/$2"
                    );

            }

            event.target.value =
                value;

        }
    );

}

/*
=========================================
DOB PICKER
=========================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const dobField =
            document.querySelector(
                "#date_of_birth"
            );

        if(dobField){

            const picker =
                flatpickr(
                    dobField,
                    {

                        dateFormat:"d/m/Y",

                        allowInput:true,

                        clickOpens:false,

                        disableMobile:true

                    }
                );

            const calendarBtn =
                document.querySelector(
                    ".dob-calendar-btn"
                );

            if(calendarBtn){

                calendarBtn.addEventListener(
                    "click",
                    () => {

                        picker.open();

                    }
                );

            }

        }

    }
);