const profileModal =
document.getElementById("profileModal");

const openProfileModal =
document.getElementById("openProfileModal");

const closeProfileModalBtn =
document.getElementById("closeProfileModal");

const cancelProfileModal =
document.getElementById("cancelProfileModal");

/* =========================
   PROFILE EDIT MODAL
========================= */

if(openProfileModal){

    openProfileModal.addEventListener(
        "click",
        ()=>{

            profileModal?.classList.add(
                "active"
            );

            document.body.style.overflow =
            "hidden";
        }
    );
}

function closeProfileModalFunc(){

    profileModal?.classList.remove(
        "active"
    );

    document.body.style.overflow = "";
}

closeProfileModalBtn?.addEventListener(
    "click",
    closeProfileModalFunc
);

cancelProfileModal?.addEventListener(
    "click",
    closeProfileModalFunc
);

profileModal?.addEventListener(
    "click",
    (e)=>{

        if(e.target === profileModal){

            closeProfileModalFunc();
        }
    }
);

/* =========================
   DP SYSTEM
========================= */

const body = document.body;

const openDpModal =
document.getElementById(
    "openDpModal"
);

const dpModal =
document.getElementById(
    "dpModal"
);

const closeDpModal =
document.getElementById(
    "closeDpModal"
);

const chooseImageBtn =
document.getElementById(
    "chooseImageBtn"
);

const profileImageInput =
document.getElementById(
    "profileImageInput"
);

const cropperModal =
document.getElementById(
    "cropperModal"
);

const cropperPreviewImage =
document.getElementById(
    "cropperPreviewImage"
);

const closeCropperModal =
document.getElementById(
    "closeCropperModal"
);

const finalCropBtn =
document.getElementById(
    "finalCropBtn"
);

const saveDpBtn =
document.getElementById(
    "saveDpBtn"
);

const currentPreviewImage =
document.getElementById(
    "currentPreviewImage"
);

const mainProfileAvatar =
document.getElementById(
    "mainProfileAvatar"
);

const csrfToken =
document.getElementById(
    "dpCsrfToken"
)?.value;

const uploadUrl =
document.getElementById(
    "profileUploadUrl"
)?.value;

let cropper = null;

let croppedBlob = null;

let croppedPreviewUrl = null;


let uploadInProgress = false;

const toastContainer =
document.getElementById(
    "toastContainer"
);


function showToast({

    type = "success",

    message = ""

}){

    const toast =
    document.createElement(
        "div"
    );

    toast.className =
    `toast ${type}`;

    const icon =

        type === "success"
        ? "✓"

        : type === "error"
        ? "✕"

        : "!";

    toast.innerHTML = `

        <div class="toast-icon">

            ${icon}

        </div>

        <div class="toast-text">

            ${message}

        </div>
    `;

    toastContainer.appendChild(
        toast
    );

    setTimeout(()=>{

        toast.classList.add(
            "hide"
        );

        setTimeout(()=>{

            toast.remove();

        },240);

    },2800);
}

function lockBody(){

    body.style.overflow = "hidden";
}


function unlockBody(){

    if(

        !dpModal.classList.contains(
            "active"
        )

        &&

        !cropperModal.classList.contains(
            "active"
        )

    ){

        body.style.overflow = "";
    }
}


function destroyCropper(){

    if(cropper){

        cropper.destroy();

        cropper = null;
    }
}


function resetDpFlow(){

    destroyCropper();

    croppedBlob = null;

    croppedPreviewUrl = null;

    profileImageInput.value = "";

    saveDpBtn.classList.add(
        "hidden"
    );

    saveDpBtn.disabled = false;

    saveDpBtn.innerText =
    "Save Changes";
}


function closeDpModalFunc(){

    dpModal.classList.remove(
        "active"
    );

    resetDpFlow();

    unlockBody();
}


function closeCropperModalFunc(){

    cropperModal.classList.remove(
        "active"
    );

    destroyCropper();

    dpModal.classList.add(
        "active"
    );

    unlockBody();
}


openDpModal?.addEventListener(

    "click",

    ()=>{

        dpModal.classList.add(
            "active"
        );

        lockBody();
    }
);


closeDpModal?.addEventListener(

    "click",

    closeDpModalFunc
);


chooseImageBtn?.addEventListener(

    "click",

    ()=>{

        profileImageInput.click();
    }
);


profileImageInput?.addEventListener(

    "change",

    (event)=>{

        const file =
        event.target.files[0];

        if(!file){

            return;
        }

        if(

            ![
                "image/jpeg",
                "image/png",
                "image/webp"
            ].includes(file.type)

        ){

            showToast({

                type:"error",

                message:
                error.message
            });

            return;
        }

        if(

            file.size >
            10 * 1024 * 1024

        ){

            showToast({

                type:"warning",

                message:
                "Maximum upload size is 10MB"
            });

            return;
        }

        const reader =
        new FileReader();

        reader.onload = ()=>{

            dpModal.classList.remove(
                "active"
            );

            cropperModal.classList.add(
                "active"
            );

            lockBody();

            cropperPreviewImage.onload =
            ()=>{

                destroyCropper();

                cropper =
                new Cropper(

                    cropperPreviewImage,

                    {

                        aspectRatio:1,

                        viewMode:1,

                        dragMode:"move",

                        autoCropArea:1,

                        responsive:true,

                        background:false,

                        guides:false,

                        center:true,

                        highlight:false
                    }
                );
            };

            cropperPreviewImage.src =
            reader.result;
        };

        reader.readAsDataURL(file);
    }
);


closeCropperModal?.addEventListener(

    "click",

    closeCropperModalFunc
);


finalCropBtn?.addEventListener(

    "click",

    ()=>{

        if(!cropper){

            return;
        }

        const canvas =
        cropper.getCroppedCanvas({

            width:600,

            height:600,

            imageSmoothingEnabled:true,

            imageSmoothingQuality:"high"
        });

        if(!canvas){

            return;
        }

        canvas.toBlob(

            (blob)=>{

                if(!blob){

                    return;
                }

                croppedBlob = blob;

                croppedPreviewUrl =
                URL.createObjectURL(blob);

                currentPreviewImage.src =
                croppedPreviewUrl;

                cropperModal.classList.remove(
                    "active"
                );

                dpModal.classList.add(
                    "active"
                );

                saveDpBtn.classList.remove(
                    "hidden"
                );

                destroyCropper();
            },

            "image/webp",

            0.92
        );
    }
);


saveDpBtn?.addEventListener(

    "click",

    async ()=>{

        if(

            !croppedBlob ||

            uploadInProgress

        ){

            return;
        }

        uploadInProgress = true;

        saveDpBtn.disabled = true;

        saveDpBtn.innerText =
        "Saving...";

        try{

            const formData =
            new FormData();

            formData.append(

                "profile_image",

                croppedBlob,

                "avatar.webp"
            );

            const response =
            await fetch(

                uploadUrl,

                {

                    method:"POST",

                    headers:{

                        "X-CSRFToken":
                        csrfToken
                    },

                    body:formData
                }
            );

            const data =
            await response.json();

            if(!response.ok){

                throw new Error(

                    data.message ||

                    "Upload failed"
                );
            }

            if(!data.success){

                throw new Error(
                    data.message
                );
            }

            mainProfileAvatar.src =
            data.image_url;

            currentPreviewImage.src =
            data.image_url;

            showToast({

                type:"success",

                message:
                "Profile picture updated"
            });

            saveDpBtn.innerText =
            "Saved";

            setTimeout(()=>{

                closeDpModalFunc();

            },500);

        }catch(error){

            console.error(error);

            showToast({

                type:"error",

                title:"Upload Failed",

                message:
                error.message ||
                "Something went wrong"
            });

            saveDpBtn.disabled =
            false;

            saveDpBtn.innerText =
            "Save Changes";

        }finally{

            uploadInProgress = false;
        }
    }
);

console.log(
    "PROFILE READY"
);


/* =========================
   DOB PICKER
========================= */

const profileDobPicker =
document.getElementById(
    "profile_date_of_birth"
);

const profileDobButton =
document.querySelector(
    ".dob-calendar-btn"
);

if(

    profileDobPicker &&

    typeof flatpickr !== "undefined"

){

    const profileDobCalendar = flatpickr(

        profileDobPicker,

        {

            dateFormat:"d/m/Y",

            allowInput:true,

            clickOpens:false,

            disableMobile:true,

            weekNumbers:false
        }
    );

    profileDobButton?.addEventListener(

        "click",

        ()=>{

            profileDobCalendar.open();
        }
    );
}



/* =========================
   BANNER CROP SYSTEM
========================= */

const bannerInput =
document.getElementById(
    "bannerInput"
);

const openBannerUpload =
document.getElementById(
    "openBannerUpload"
);

const bannerCropModal =
document.getElementById(
    "bannerCropModal"
);

const bannerCropImage =
document.getElementById(
    "bannerCropImage"
);

const closeBannerCropModal =
document.getElementById(
    "closeBannerCropModal"
);

const cropBannerBtn =
document.getElementById(
    "cropBannerBtn"
);

const profileCover =
document.querySelector(
    ".profile-cover"
);

const bannerUploadUrl =
document.getElementById(
    "bannerUploadUrl"
)?.value;

let bannerCropper = null;

/* OPEN FILE PICKER */

openBannerUpload?.addEventListener(

    "click",

    ()=>{

        bannerInput?.click();
    }
);

/* SELECT IMAGE */

bannerInput?.addEventListener(

    "change",

    (event)=>{

        const file =
        event.target.files[0];

        if(!file){

            return;
        }

        const reader =
        new FileReader();

        reader.onload =
        (e)=>{

            bannerCropImage.src =
            e.target.result;

            bannerCropModal.classList.add(
                "active"
            );

            bannerCropImage.onload =
            ()=>{

                if(bannerCropper){

                    bannerCropper.destroy();
                }

                bannerCropper =
                new Cropper(

                    bannerCropImage,

                    {

                        aspectRatio:16/5,

                        viewMode:1,

                        dragMode:"move",

                        autoCropArea:1,

                        responsive:true,

                        background:false
                    }
                );
            };
        };

        reader.readAsDataURL(file);

    }
);

/* CLOSE MODAL */

closeBannerCropModal?.addEventListener(

    "click",

    ()=>{

        bannerCropModal.classList.remove(
            "active"
        );

        if(bannerCropper){

            bannerCropper.destroy();

            bannerCropper = null;
        }
    }
);

/* SAVE CROPPED BANNER */

cropBannerBtn?.addEventListener(

    "click",

    ()=>{

        if(!bannerCropper){

            return;
        }

        cropBannerBtn.disabled = true;

        cropBannerBtn.innerText =
        "Saving...";

        const canvas =
        bannerCropper.getCroppedCanvas({

            width:1600,

            height:500
        });

        canvas.toBlob(

            async(blob)=>{

                try{

                    const formData =
                    new FormData();

                    formData.append(

                        "banner",

                        blob,

                        "banner.webp"
                    );

                    const response =
                    await fetch(

                        bannerUploadUrl,

                        {

                            method:"POST",

                            headers:{

                                "X-CSRFToken":
                                csrfToken
                            },

                            body:formData
                        }
                    );

                    const data =
                    await response.json();

                    if(!response.ok){

                        throw new Error(

                            data.message ||

                            "Banner upload failed"
                        );
                    }

                    profileCover.style.backgroundImage =

                    `linear-gradient(
                    135deg,
                    rgba(139,92,246,.25),
                    rgba(15,23,42,.15)
                    ), url(${data.banner_url}?v=${Date.now()})`;

                    bannerCropModal.classList.remove(
                        "active"
                    );

                    bannerCropper.destroy();

                    bannerCropper = null;

                    showToast({

                        type:"success",

                        message:
                        "Banner updated successfully"
                    });

                }

                catch(error){

                    console.error(error);

                    showToast({

                        type:"error",

                        message:
                        "Banner upload failed"
                    });
                }

                cropBannerBtn.disabled = false;

                cropBannerBtn.innerText =
                "Save Banner";

            },

            "image/webp",

            .95
        );
    }
);