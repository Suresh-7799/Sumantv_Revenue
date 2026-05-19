const roleSelect =
document.getElementById(
    "roleSelect"
);

const customRoleInput =
document.getElementById(
    "customRoleInput"
);

if(roleSelect && customRoleInput){

    roleSelect.addEventListener(
        "change",
        function(){

            if(this.value === "custom"){

                customRoleInput
                .classList
                .add("active");

                customRoleInput.focus();

            }else{

                customRoleInput
                .classList
                .remove("active");

                customRoleInput.value = "";
            }

        }
    );

}


/* =========================
   DOB PICKER
========================= */

const adminDobPicker =
document.getElementById(
    "admin_date_of_birth"
);

const adminDobButton =
document.querySelector(
    ".dob-calendar-btn"
);

if(

    adminDobPicker &&

    typeof flatpickr !== "undefined"

){

    const adminDobCalendar = flatpickr(

        adminDobPicker,

        {

            dateFormat:"d/m/Y",

            allowInput:true,

            clickOpens:false,

            disableMobile:true,

            weekNumbers:false
        }
    );

    adminDobButton?.addEventListener(

        "click",

        ()=>{

            adminDobCalendar.open();
        }
    );
}