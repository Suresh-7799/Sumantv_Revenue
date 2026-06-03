document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        const channelSelect = document.getElementById(
            "channelSelect"
        );

        const openChannelBtn = document.getElementById(
            "openChannelBtn"
        );

        const openChannelModal = document.getElementById(
            "openChannelModal"
        );

        const closeChannelModal = document.getElementById(
            "closeChannelModal"
        );

        const channelModal = document.getElementById(
            "channelModal"
        );

        const exportBtn = document.getElementById(
            "exportBtn"
        );

        const exportModal = document.getElementById(
            "exportModal"
        );

        const closeExportModal = document.getElementById(
            "closeExportModal"
        );

        let activeEditRow = null;

        let activeDeleteRow = null;

        openChannelBtn?.addEventListener(

            "click",

            ()=>{

                const selectedOption =

                    channelSelect.options[
                        channelSelect.selectedIndex
                    ];

                const channelUrl =

                    selectedOption?.dataset?.url;

                if(
                    !channelUrl
                ){
                    return;
                }

                window.open(
                    channelUrl,
                    "_blank"
                );
            }
        );

        openChannelModal?.addEventListener(

            "click",

            ()=>{

                channelModal?.classList.add(
                    "active"
                );
            }
        );

        closeChannelModal?.addEventListener(

            "click",

            ()=>{

                channelModal?.classList.remove(
                    "active"
                );
            }
        );

        exportBtn?.addEventListener(

            "click",

            ()=>{

                exportModal.classList.add(
                    "active"
                );
            }
        );

        closeExportModal?.addEventListener(

            "click",

            ()=>{

                exportModal.classList.remove(
                    "active"
                );
            }
        );

        document.querySelectorAll(

            ".channel-accordion-header"

        ).forEach(

            header=>{

                header.addEventListener(

                    "click",

                    ()=>{

                        const channelId =

                            header.dataset.channel;

                        const currentBody =

                            document.getElementById(
                                `channel-body-${channelId}`
                            );

                        document.querySelectorAll(

                            ".channel-accordion-body"

                        ).forEach(

                            body=>{

                                if(

                                    body !== currentBody
                                ){

                                    body.classList.remove(
                                        "active"
                                    );
                                }
                            }
                        );

                        currentBody.classList.toggle(
                            "active"
                        );
                    }
                );
            }
        );

        document.querySelectorAll(

            ".edit-link-btn"

        ).forEach(

            button=>{

                button.addEventListener(

                    "click",

                    ()=>{

                        if(

                            activeDeleteRow
                        ){

                            showTrackingToast(

                                "Finish delete action first",

                                "warning"
                           );

                            return;
                        }

                        const row =

                            button.closest(
                                "tr"
                            );

                        activeEditRow = row;

                        const rowId =

                            row.dataset.id;

                        const stripCell =

                            row.querySelector(
                                ".strip-cell"
                            );

                        const linkCell =

                            row.querySelector(
                                ".link-cell"
                            );

                        const dateCell =

                            row.querySelector(
                                ".date-cell"
                            );

                        if(

                            button.classList.contains(
                                "save-mode"
                            )
                        ){

                            fetch(

                                "/workspace/edit-tracking-link",

                                {

                                    method:"POST",

                                    headers:{

                                        "Content-Type":
                                        "application/json",

                                        "X-CSRFToken":
                                        document.querySelector(
                                            'input[name="csrf_token"]'
                                        ).value
                                    },

                                    body:JSON.stringify({

                                        id:rowId,

                                        strip_name:
                                        row.querySelector(
                                            ".inline-edit-strip"
                                        ).value,

                                        video_url:
                                        row.querySelector(
                                            ".inline-edit-link"
                                        ).value,

                                        published_date:
                                        row.querySelector(
                                            ".inline-edit-date"
                                        ).value
                                    })
                                }
                            )

                            .then(

                                r=>{

                                    console.log(
                                        "STATUS",
                                        r.status
                                    );

                                    return r.json();
                                }
                            )

                            .then(

                                data=>{

                                    if(
                                        data.success
                                    ){
                                        showTrackingToast(
                                            "Updated Successfully"
                                        );

                                        activeEditRow = null;

                                        stripCell.innerHTML =
                                            row.querySelector(
                                                ".inline-edit-strip"
                                            ).value;

                                        linkCell.innerHTML =
                                            row.querySelector(
                                                ".inline-edit-link"
                                            ).value;

                                        dateCell.innerHTML =
                                            row.querySelector(
                                                ".inline-edit-date"
                                            ).value;

                                        button.innerHTML =
                                            "✎";

                                        button.classList.remove(
                                            "save-mode"
                                        );

                                        row.querySelector(
                                            ".cancel-edit-btn"
                                        )?.remove();
                                    }
                                }
                            );

                            return;
                        }

                        const originalStrip =

                            stripCell.textContent.trim();

                        const originalLink =

                            linkCell.textContent.trim();

                        const originalDate =

                            dateCell.textContent.trim();

                        stripCell.innerHTML =

                            `<input class="inline-edit-strip" value="${originalStrip}">`;

                        linkCell.innerHTML =

                            `<input class="inline-edit-link" value="${originalLink}">`;

                        dateCell.innerHTML =

                            `<input class="inline-edit-date" value="${originalDate}">`;

                        button.innerHTML =
                            "✓";

                        button.classList.add(
                            "save-mode"
                        );

                        row.querySelector(

                            ".cancel-edit-btn"

                        )?.remove();

                        const cancelBtn =

                            document.createElement(
                                "button"
                            );

                        cancelBtn.type =
                            "button";

                        cancelBtn.innerHTML =
                            "✕";

                        cancelBtn.className =
                            "cancel-edit-btn";

                        cancelBtn.style.marginLeft =
                            "8px";

                        button.after(
                            cancelBtn
                        );

                        cancelBtn.addEventListener(

                            "click",

                            ()=>{

                                activeEditRow = null;

                                stripCell.innerHTML =
                                    originalStrip;

                                linkCell.innerHTML =
                                    originalLink;

                                dateCell.innerHTML =
                                    originalDate;

                                button.innerHTML =
                                    "✎";

                                button.classList.remove(
                                    "save-mode"
                                );

                                cancelBtn.remove();
                            }
                        );
                    }
                );
            }
        );

        document.querySelectorAll(

            ".delete-link-btn"

        ).forEach(

            button=>{

                button.addEventListener(

                    "click",

                    ()=>{

                        if(

                            activeEditRow
                        ){

                            showTrackingToast(

                                "Finish editing first",

                                "warning"
                            );

                            return;
                        }

                        const row =

                            button.closest(
                                "tr"
                            );

                        activeDeleteRow = row;

                        const rowId =

                            row.dataset.id;

                        if(

                            button.classList.contains(
                                "confirm-delete"
                            )
                        ){

                            fetch(

                                "/workspace/delete-tracking-link",

                                {

                                    method:"POST",

                                    headers:{

                                        "Content-Type":
                                        "application/json",

                                        "X-CSRFToken":
                                        document.querySelector(
                                            'input[name="csrf_token"]'
                                        ).value
                                    },

                                    body:JSON.stringify({

                                        id:rowId
                                    })
                                }
                            )

                            .then(

                                r=>{

                                    console.log(
                                        "STATUS",
                                        r.status
                                    );

                                    return r.json();
                                }
                            )

                            .then(

                                data=>{

                                    if(
                                        data.success
                                    ){

                                      showTrackingToast(
                                          "Deleted Successfully"
                                      );

                                    activeDeleteRow = null;

                                        row.remove();
                                    }
                                }
                            );

                            return;
                        }

                        button.innerHTML =
                            "✓";

                        button.classList.add(
                            "confirm-delete"
                        );

                        const cancelBtn =

                            document.createElement(
                                "button"
                            );

                        cancelBtn.type =
                            "button";

                        cancelBtn.innerHTML =
                            "✕";

                        cancelBtn.className =
                            "cancel-delete-btn";

                        button.after(
                            cancelBtn
                        );

                        cancelBtn.addEventListener(

                            "click",

                            ()=>{

                                button.innerHTML =
                                    "🗑";

                                button.classList.remove(
                                    "confirm-delete"
                                );

                                cancelBtn.remove();
                                activeDeleteRow = null;
                            }
                        );
                    }
                );
            }
        );

        document.getElementById(

            "exportSelectedChannel"

        )?.addEventListener(

            "click",

            ()=>{

                window.location.href =

                    "/workspace/export-tracking";
            }
        );

        document.getElementById(

            "exportAllChannels"

        )?.addEventListener(

            "click",

            ()=>{

                window.location.href =

                    "/workspace/export-tracking";
            }
        );

    }
);

function showTrackingToast(

    message,

    type="success"
){

    const oldToast =

        document.querySelector(
            ".tracking-toast"
        );

    oldToast?.remove();

    const toast =

        document.createElement(
            "div"
        );

    toast.className =
        `tracking-toast ${type}`;

    toast.textContent =
        message;

    document.body.appendChild(
        toast
    );

    setTimeout(

        ()=>{

            toast.classList.add(
                "show"
            );
        },

        10
    );

    setTimeout(

        ()=>{

            toast.remove();
        },

        2500
    );
}