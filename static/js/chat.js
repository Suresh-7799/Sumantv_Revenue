window.addEventListener(

    "load",

    ()=>{

        initializeChat();
    }
);

function initializeChat(){

    console.log(
        "CHAT INIT STARTED"
    );

    /* =========================
       SAFETY CHECKS
    ========================= */

    if(!window.socket){

        console.error(
            "Socket missing"
        );

        return;
    }

    if(typeof CURRENT_USER_ID === "undefined"){

        console.error(
            "CURRENT_USER_ID missing"
        );

        return;
    }

    /* =========================
       GLOBALS
    ========================= */

    const socket = window.socket;

    const csrfToken = document
    .querySelector(
        'meta[name="csrf-token"]'
    )
    ?.getAttribute("content");

    /* =========================
       ELEMENTS
    ========================= */

    const chatFab =
    document.getElementById(
        "chatFab"
    );

    const chatDrawer =
    document.getElementById(
        "chatDrawer"
    );

    const closeChatDrawer =
    document.getElementById(
        "closeChatDrawer"
    );

    const chatConversation =
    document.getElementById(
        "chatConversation"
    );

    const activeChatUser =
    document.getElementById(
        "activeChatUser"
    );

    const chatMessages =
    document.getElementById(
        "chatMessages"
    );

    const sendChatMessage =
    document.getElementById(
        "sendChatMessage"
    );

    const chatMessageInput =
    document.getElementById(
        "chatMessageInput"
    );

    const chatUserSearch =
    document.getElementById(
        "chatUserSearch"
    );

    const attachChatFile =
    document.getElementById(
        "attachChatFile"
    );

    const chatFileInput =
    document.getElementById(
        "chatFileInput"
    );

    const chatMenuBtn =
    document.getElementById(
        "chatMenuBtn"
    );

    const chatMenuDropdown =
    document.getElementById(
        "chatMenuDropdown"
    );

    const backToUsers =
    document.getElementById(
        "backToUsers"
    );

    const viewProfileBtn =
    document.getElementById(
        "viewProfileBtn"
    );

    /* =========================
       STATES
    ========================= */

    let activeReceiverId = null;

    let uploadedFile = null;

    let uploadInProgress = false;

    let readThrottle = false;

    let typingTimeout;

    window.chatUsers = [];

    /* =========================
       SOCKET CLEANUP
    ========================= */

    socket.off("connect");
    socket.off("receive_message");
    socket.off("message_deleted");
    socket.off("chat_cleared");
    socket.off("user_typing");
    socket.off("message_read");
    socket.off("chat_error");
    socket.off("disconnect");
    socket.off("reconnect");

    /* =========================
       SOCKET CONNECT
    ========================= */

    socket.on(

        "connect",

        async ()=>{

            console.log(
                "SOCKET CONNECTED:",
                socket.id
            );

            if(activeReceiverId){

                socket.emit(

                    "join_chat",

                    {
                        receiver_id:
                        activeReceiverId
                    }
                );

                await loadMessages();
            }
        }
    );


/* =========================
   RECEIVE MESSAGE
========================= */

socket.on(

    "receive_message",

    (data)=>{

        const senderId = Number(
            data.sender_id
        );

        const receiverId = Number(
            data.receiver_id
        );

        const currentId = Number(
            CURRENT_USER_ID
        );

        const belongsToCurrentChat =

            (
                senderId === activeReceiverId
                &&
                receiverId === currentId
            )

            ||

            (
                senderId === currentId
                &&
                receiverId === activeReceiverId
            );

        if(!belongsToCurrentChat){

            return;
        }

        appendMessage(data);
    }
);


/* =========================
   MESSAGE DELETE
========================= */

socket.on(

    "message_deleted",

    (data)=>{

        const message = document.querySelector(

            `.chat-message[data-message-id="${data.message_id}"]`
        );

        if(message){

            message.remove();
        }
    }
);


/* =========================
   CHAT CLEARED
========================= */

socket.on(

    "chat_cleared",

    ()=>{

        if(chatMessages){

            chatMessages.innerHTML = "";
        }
    }
);


/* =========================
   READ RECEIPTS
========================= */

socket.on(

    "message_read",

    (data)=>{

        const message =

        document.querySelector(

            `[data-message-id="${data.message_id}"]`
        );

        if(!message){

            return;
        }

        message.classList.add(
            "read"
        );
    }
);


/* =========================
   TYPING INDICATOR
========================= */

socket.on(

    "user_typing",

    ()=>{

        const typingEl =
        document.getElementById(
            "chatTypingIndicator"
        );

        if(!typingEl){

            return;
        }

        typingEl.style.display =
        "block";

        clearTimeout(
            typingTimeout
        );

        typingTimeout = setTimeout(

            ()=>{

                typingEl.style.display =
                "none";
            },

            1500
        );
    }
);


/* =========================
   SOCKET ERRORS
========================= */

socket.on(

    "chat_error",

    (data)=>{

        console.error(
            data.message
        );

        alert(
            data.message ||
            "Chat error"
        );
    }
);


/* =========================
   SOCKET DISCONNECT
========================= */

socket.on(

    "disconnect",

    ()=>{

        console.warn(
            "Socket disconnected"
        );
    }
);


/* =========================
   SOCKET RECONNECT
========================= */

socket.on(

    "reconnect",

    async ()=>{

        console.log(
            "Socket reconnected"
        );

        if(activeReceiverId){

            socket.emit(

                "join_chat",

                {
                    receiver_id:
                    activeReceiverId
                }
            );

            setTimeout(

                async ()=>{

                    await loadMessages();

                },

                300
            );
        }
    }
);


/* =========================
   OPEN / CLOSE DRAWER
========================= */

if(chatFab){

    chatFab.onclick = (e)=>{

        e.stopPropagation();

        chatDrawer?.classList.toggle(
            "active"
        );
    };
}


/* =========================
   OUTSIDE CLICK
========================= */

window.addEventListener(

    "click",

    (e)=>{

        const clickedFab = e.target.closest(
            "#chatFab"
        );

        const clickedDrawer = e.target.closest(
            "#chatDrawer"
        );

        const popup = e.target.closest(
            "#chatDeletePopup"
        );

        if(
            clickedFab
            ||
            clickedDrawer
            ||
            popup
        ){

            return;
        }

        chatDrawer?.classList.remove(
            "active"
        );

        chatMenuDropdown?.classList.remove(
            "active"
        );
    }
);


/* =========================
   CLOSE DRAWER
========================= */

closeChatDrawer?.addEventListener(

    "click",

    ()=>{

        chatDrawer?.classList.remove(
            "active"
        );

        chatConversation?.classList.remove(
            "active"
        );

        if(chatMessages){

            chatMessages.innerHTML = "";
        }
    }
);


/* =========================
   BACK BUTTON
========================= */

backToUsers?.addEventListener(

    "click",

    ()=>{

        chatConversation?.classList.remove(
            "active"
        );

        activeReceiverId = null;
    }
);


/* =========================
   SEARCH USERS
========================= */

chatUserSearch?.addEventListener(

    "input",

    ()=>{

        const value =

        chatUserSearch.value
        .toLowerCase();

        document
        .querySelectorAll(
            ".chat-user-item"
        )
        .forEach(item=>{

            const name =

                (
                    item.dataset.name || ""
                )
                .toLowerCase();

            item.style.display =

                name.includes(value)

                ? "flex"

                : "none";
        });
    }
);


/* =========================
   LOAD MESSAGES
========================= */

async function loadMessages(){

    if(!activeReceiverId){

        return;
    }

    try{

        const response = await fetch(

            `/chat/messages/${activeReceiverId}`
        );

        if(!response.ok){

            return;
        }

        const messages =
        await response.json();

        if(!Array.isArray(messages)){

            return;
        }

        if(chatMessages){

            chatMessages.innerHTML = "";
        }

        messages.forEach(msg=>{

            appendMessage(msg);
        });

        scrollMessages();
    }

    catch(error){

        console.error(
            "LOAD FAILED:",
            error
        );
    }
}


/* =========================
   GLOBAL CLICK EVENTS
========================= */

document.addEventListener(

    "click",

    async (e)=>{

        const userItem =

        e.target.closest(
            ".chat-user-item"
        );

        const messageMenuBtn =

        e.target.closest(
            ".chat-message-menu-btn"
        );

        const dropdownContent =

        e.target.closest(
            ".chat-message-dropdown"
        );

        if(dropdownContent){

            e.stopPropagation();

            return;
        }

        const profileModal =

        document.getElementById(
            "chatProfileModal"
        );

        /* =========================
           OPEN USER CHAT
        ========================= */

        if(userItem){

            const userId = Number(
                userItem.dataset.userId
            );

            const existingUser =

                window.chatUsers.find(
                    user => Number(user.id) === userId
                );

            if(!existingUser){

                window.chatUsers.push({

                    id:
                    userId,

                    username:
                    userItem.dataset.name,

                    avatar:
                    userItem.dataset.avatar
                });
            }

            activeReceiverId = userId;

            if(activeChatUser){

                activeChatUser.innerText =
                userItem.dataset.name || "";
            }

            const avatar =
            document.getElementById(
                "activeChatAvatar"
            );

            if(avatar){

                avatar.src =
                userItem.dataset.avatar || "";
            }

            chatConversation?.classList.add(
                "active"
            );

            socket.emit(

                "join_chat",

                {
                    receiver_id:
                    activeReceiverId
                }
            );

            await loadMessages();

            return;
        }

        /* =========================
           MESSAGE DROPDOWN
        ========================= */

        if(messageMenuBtn){

            e.stopPropagation();

            const dropdown =

            messageMenuBtn
            .closest(
                ".chat-message-actions"
            )

            ?.querySelector(
                ".chat-message-dropdown"
            );

            document
            .querySelectorAll(
                ".chat-message-dropdown"
            )
            .forEach(drop=>{

                if(drop !== dropdown){

                    drop.classList.remove(
                        "active"
                    );
                }
            });

            dropdown?.classList.toggle(
                "active"
            );

            return;
        }

        /* =========================
           CLOSE MENUS
        ========================= */

        document
        .querySelectorAll(
            ".chat-message-dropdown"
        )
        .forEach(drop=>{

            drop.classList.remove(
                "active"
            );
        });

        chatMenuDropdown?.classList.remove(
            "active"
        );

        /* =========================
           CLOSE PROFILE MODAL
        ========================= */

        if(

            profileModal
            &&
            e.target === profileModal
        ){

            profileModal.classList.remove(
                "active"
            );
        }
    }
);


/* =========================
   VIEW PROFILE
========================= */

viewProfileBtn?.addEventListener(

    "click",

    async ()=>{

        if(!activeReceiverId){

            return;
        }

        try{

            const response = await fetch(

                `/chat/user/${activeReceiverId}`
            );

            if(!response.ok){

                return;
            }

            const user =
            await response.json();

            const modal =

            document.getElementById(
                "chatProfileModal"
            );

            if(!modal){

                return;
            }

            modal.classList.add(
                "active"
            );

            const avatar =
            document.getElementById(
                "chatProfileAvatar"
            );

            const banner =
            document.getElementById(
                "chatProfileBanner"
            );

            if(avatar){

                avatar.src =

                    user.profile_image ||

                    "/static/default-avatar.png";
            }

            if(banner){

                if(user.banner){

                    banner.src =
                    user.banner;

                    banner.style.display =
                    "block";
                }

                else{

                    banner.removeAttribute(
                        "src"
                    );

                    banner.style.display =
                    "none";
                }
            }

            const fullNameEl =
            document.getElementById(
                "chatProfileFullName"
            );

            if(fullNameEl){

                fullNameEl.innerText =
                user.full_name || "-";
            }

            const firstNameEl =
            document.getElementById(
                "chatProfileFirstName"
            );

            if(firstNameEl){

                firstNameEl.innerText =
                user.first_name || "-";
            }

            const lastNameEl =
            document.getElementById(
                "chatProfileLastName"
            );

            if(lastNameEl){

                lastNameEl.innerText =
                user.last_name || "-";
            }

            const emailEl =
            document.getElementById(
                "chatProfileEmail"
            );

            if(emailEl){

                emailEl.innerText =
                user.email || "-";
            }

            const employeeIdEl =
            document.getElementById(
                "chatProfileEmployeeId"
            );

            if(employeeIdEl){

                employeeIdEl.innerText =
                user.employee_id || "-";
            }

            const roleEl =
            document.getElementById(
                "chatProfileRole"
            );

            if(roleEl){

                roleEl.innerText =
                user.role || "-";
            }
        }

        catch(error){

            console.error(
                "PROFILE LOAD ERROR:",
                error
            );
        }
    }
);


/* =========================
   FILE ATTACH
========================= */

attachChatFile?.addEventListener(

    "click",

    ()=>{

        if(uploadInProgress){

            return;
        }

        chatFileInput?.click();
    }
);


/* =========================
   FILE UPLOAD
========================= */

chatFileInput?.addEventListener(

    "change",

    ()=>{

        const file =
        chatFileInput.files?.[0];

        if(!file){

            return;
        }

        const allowedMimeTypes = [

            "image/png",
            "image/jpeg",
            "image/webp",
            "image/gif",

            "video/mp4",
            "video/webm",
            "video/quicktime",

            "application/pdf",

            "application/zip",
            "application/x-zip-compressed"
        ];

        if(

            !allowedMimeTypes.includes(
                file.type
            )
        ){

            alert(
                "Unsupported file type"
            );

            chatFileInput.value = "";

            return;
        }

        if(file.size > 30 * 1024 * 1024){

            alert(
                "Max upload size is 30MB"
            );

            chatFileInput.value = "";

            return;
        }

        uploadChatFile(file);
    }
);


/* =========================
   FILE UPLOAD REQUEST
========================= */

async function uploadChatFile(file){

    uploadInProgress = true;

    const formData =
    new FormData();

    formData.append(
        "file",
        file
    );

    try{

        const xhr =
        new XMLHttpRequest();

        xhr.open(

            "POST",

            "/chat/upload"
        );

        xhr.setRequestHeader(

            "X-CSRFToken",

            csrfToken
        );

        xhr.upload.addEventListener(

            "progress",

            (e)=>{

                if(e.lengthComputable){

                    const percent = Math.round(

                        (
                            e.loaded
                            /
                            e.total
                        ) * 100
                    );

                    console.log(

                        "UPLOAD:",

                        percent + "%"
                    );
                }
            }
        );

        xhr.onload = ()=>{

            uploadInProgress = false;

            try{

                const data = JSON.parse(
                    xhr.responseText
                );

                if(!data.success){

                    alert(

                        data.message ||

                        "Upload failed"
                    );

                    chatFileInput.value = "";

                    return;
                }

                uploadedFile =
                data.file;

                console.log(

                    "FILE READY:",

                    uploadedFile
                );

                chatFileInput.value = "";
            }

            catch(error){

                console.error(
                    error
                );

                chatFileInput.value = "";
            }
        };

        xhr.onerror = ()=>{

            uploadInProgress = false;

            chatFileInput.value = "";

            alert(
                "Upload failed"
            );
        };

        xhr.send(formData);
    }

    catch(error){

        uploadInProgress = false;

        chatFileInput.value = "";

        console.error(
            error
        );
    }
}


/* =========================
   SEND MESSAGE
========================= */

function sendMessage(){

    if(uploadInProgress){

        return;
    }

    const message =

        (
            chatMessageInput?.value || ""
        )
        .trim();

    if(message.length > 5000){

        alert(
            "Message too long"
        );

        return;
    }

    if(

        !message
        &&
        !uploadedFile
    ){

        return;
    }

    if(!activeReceiverId){

        return;
    }

    if(!socket.connected){

        alert(
            "Connection lost"
        );

        return;
    }

    console.log(

        "SENDING MESSAGE",

        {
            receiver_id:
            activeReceiverId,

            message:
            message
        }
    );

    socket.emit(

        "send_message",

        {

            receiver_id:
            activeReceiverId,

            message:
            message,

            file:
            uploadedFile
        }
    );

    if(chatMessageInput){

        chatMessageInput.value = "";
    }

    uploadedFile = null;

    if(chatFileInput){

        chatFileInput.value = "";
    }
}


/* =========================
   SEND BUTTON
========================= */

sendChatMessage?.addEventListener(

    "click",

    ()=>{

        sendMessage();
    }
);


/* =========================
   ENTER SEND
========================= */

chatMessageInput?.addEventListener(

    "keydown",

    (e)=>{

        if(

            e.key === "Enter"
            &&
            !e.shiftKey
        ){

            e.preventDefault();

            sendMessage();
        }
    }
);


/* =========================
   TYPING
========================= */

let typingThrottle = false;

chatMessageInput?.addEventListener(

    "input",

    ()=>{

        if(!activeReceiverId){

            return;
        }

        if(!socket.connected){

            return;
        }

        if(typingThrottle){

            return;
        }

        typingThrottle = true;

        socket.emit(

            "typing",

            {
                receiver_id:
                activeReceiverId
            }
        );

        setTimeout(

            ()=>{

                typingThrottle = false;

            },

            1200
        );
    }
);

/* =========================
   APPEND MESSAGE
========================= */

let lastMessageDate = null;

function appendMessage(data){

    if(!data){

        return;
    }

    if(data.deleted){

        return;
    }

    const currentDate =
    data.full_date || "";

    if(

        currentDate
        &&
        currentDate !== lastMessageDate
    ){

        const separator =
        document.createElement("div");

        separator.className =
        "chat-date-separator";

        separator.innerHTML = `
            <span>${currentDate}</span>
        `;

        chatMessages?.appendChild(
            separator
        );

        lastMessageDate =
        currentDate;
    }

    if(data.id){

        const existing =

        document.querySelector(

            `[data-message-id="${data.id}"]`
        );

        if(existing){

            return;
        }
    }

    const div =
    document.createElement("div");

    const isMine =

        Number(data.sender_id)

        ===

        Number(CURRENT_USER_ID);

    div.className =

        isMine

        ?

        "chat-message me"

        :

        "chat-message other";

    div.dataset.messageId =
    data.id;

    /* =========================
       FILE HTML
    ========================= */

    let fileHtml = "";

    if(data.file_url){

        const mimeType = (
            data.file_type || ""
        ).toLowerCase();

        const isImage =
        mimeType.startsWith(
            "image/"
        );

        const isVideo =
        mimeType.startsWith(
            "video/"
        );

        if(isImage){

            fileHtml = `

                <img
                src="${data.file_url}"
                class="chat-image-preview"
                alt="Image">
            `;
        }

        else if(isVideo){

            fileHtml = `

                <video
                controls
                class="chat-video-preview">

                    <source
                    src="${data.file_url}">
                </video>
            `;
        }

        else{

            fileHtml = `

                <a
                href="${data.file_url}"
                target="_blank"
                class="chat-file-link">

                    📎
                    ${escapeHtml(
                        data.file_name || "File"
                    )}

                </a>
            `;
        }
    }

    /* =========================
       ACTIONS MENU
    ========================= */

    const actionsMenu =

        isMine

        ?

        `

        <div class="chat-message-actions">

            <button
            class="chat-message-menu-btn"
            type="button">

                <i data-lucide="more-horizontal"></i>

            </button>

            <div
            class="chat-message-dropdown">

                <button
                type="button"
                class="copy-message-btn"
                data-message="${escapeHtml(data.message || "")}">

                    Copy

                </button>

                <button
                type="button"
                class="forward-message-btn"
                data-id="${data.id}">

                    Forward

                </button>

                <button
                type="button"
                class="delete-message-btn"
                data-id="${data.id}">

                    Delete

                </button>

            </div>

        </div>

        `

        :

        "";

    /* =========================
       MESSAGE HTML
    ========================= */

    div.innerHTML = `

        <div class="chat-message-bubble">

            ${actionsMenu}

            ${fileHtml}

            ${data.message ? `

                <div class="chat-message-text">

                    ${escapeHtml(
                        data.message
                    )}

                </div>

            ` : ""}

            <div class="chat-message-footer">

                <div class="chat-message-time">

                    ${data.created_at || ""}

                </div>

            </div>

        </div>
    `;

    if(chatMessages){

        chatMessages.appendChild(
            div
        );
    }

    if(window.lucide){

        lucide.createIcons();
    }

    scrollMessages();
}


/* =========================
   DELETE POPUP
========================= */

function openDeletePopup(messageId){

    let popup = document.getElementById(
        "chatDeletePopup"
    );

    if(popup){

        popup.remove();
    }

    popup = document.createElement(
        "div"
    );

    popup.id =
    "chatDeletePopup";

    popup.className =
    "chat-delete-popup active";

    document
    .querySelectorAll(
        ".chat-message-dropdown"
    )
    .forEach(drop=>{

        drop.classList.remove(
            "active"
        );
    });

    popup.innerHTML = `

        <div class="chat-delete-popup-card">

            <h4>
                Delete message?
            </h4>

            <button
            class="chat-delete-option"
            data-type="me">

                Delete for me

            </button>

            <button
            class="chat-delete-option danger"
            data-type="everyone">

                Unsend

            </button>

            <button
            class="chat-delete-cancel">

                Cancel

            </button>

        </div>
    `;

    chatConversation?.appendChild(
        popup
    );

    /* =========================
       DELETE / UNSEND
    ========================= */

    popup
    .querySelectorAll(
        ".chat-delete-option"
    )
    .forEach(btn=>{

        btn.onclick = async (e)=>{

            e.preventDefault();

            e.stopPropagation();

            const type =
            btn.dataset.type;

            const endpoint =

                type === "everyone"

                ?

                "/chat/delete-message"

                :

                "/chat/delete-for-me";

            try{

                const response =
                await fetch(

                    endpoint,

                    {

                        method:"POST",

                        headers:{

                            "Content-Type":
                            "application/json",

                            "X-CSRFToken":
                            csrfToken
                        },

                        body:JSON.stringify({

                            message_id:
                            messageId
                        })
                    }
                );

                if(response.ok){

                    const messageElement =

                    document.querySelector(

                        `.chat-message[data-message-id="${messageId}"]`
                    );

                    if(messageElement){

                        messageElement.remove();
                    }

                    popup.remove();
                }

                else{

                    alert(
                        "Delete failed"
                    );
                }
            }

            catch(error){

                console.error(
                    error
                );
            }
        };
    });

    /* =========================
       CANCEL
    ========================= */

    popup.querySelector(
        ".chat-delete-cancel"
    ).onclick = (e)=>{

        e.preventDefault();

        e.stopPropagation();

        popup.remove();
    };
}


/* =========================
   COPY MESSAGE
========================= */

document.addEventListener(

    "click",

    async (e)=>{

        const copyBtn =

        e.target.closest(
            ".copy-message-btn"
        );

        if(!copyBtn){

            return;
        }

        const message =

            copyBtn.dataset.message || "";

        try{

            await navigator.clipboard
            .writeText(message);

            console.log(
                "Copied"
            );

            showChatToast(
                "Copied"
            );

            document
            .querySelectorAll(
                ".chat-message-dropdown"
            )
            .forEach(drop=>{

                drop.classList.remove(
                    "active"
                );
            });
        }

        catch(error){

            console.error(
                error
            );
        }
    }
);


/* =========================
   CHAT TOAST
========================= */

function showChatToast(message){

    let toast = document.querySelector(
        ".chat-toast"
    );

    if(toast){

        toast.remove();
    }

    toast = document.createElement(
        "div"
    );

    toast.className =
    "chat-toast";

    toast.innerText =
    message;

    chatConversation?.appendChild(
        toast
    );

    setTimeout(

        ()=>{

            toast.classList.add(
                "active"
            );

        },

        10
    );

    setTimeout(

        ()=>{

            toast.classList.remove(
                "active"
            );

            setTimeout(

                ()=>{

                    toast.remove();

                },

                200
            );

        },

        1600
    );
}

/* =========================
   FORWARD PANEL
========================= */

function openForwardPanel(

    messageId,

    messageText
){

    const oldPanel =
    document.querySelector(
        ".chat-forward-panel"
    );

    if(oldPanel){

        oldPanel.remove();
    }

    document
    .querySelectorAll(
        ".chat-message-dropdown"
    )
    .forEach(drop=>{

        drop.classList.remove(
            "active"
        );
    });

    const panel =
    document.createElement(
        "div"
    );

    panel.className =
    "chat-forward-panel";

    panel.innerHTML = `

        <div class="chat-forward-top">

            <h4>
                Forward message
            </h4>

            <button
            class="chat-forward-close">

                ✕

            </button>

        </div>

        <input
        type="text"
        class="chat-forward-search"
        placeholder="Search users..."
        />

        <div class="chat-forward-users">

            ${window.chatUsers?.map(user=>`

                <button

                class="chat-forward-user"

                data-id="${user.id}"

                data-name="${user.username}">

                    <img
                    src="${user.avatar || "/static/default-avatar.png"}"
                    alt="Avatar">

                    <span>

                        ${user.username}

                    </span>

                </button>

            `).join("") || ""}

        </div>

        <button
        class="chat-forward-send">

            Send Forward

        </button>
    `;

    chatConversation?.appendChild(
        panel
    );

    const selectedUsers =
    new Set();

    /* =========================
       SELECT USERS
    ========================= */

    panel.querySelectorAll(
        ".chat-forward-user"
    ).forEach(btn=>{

        btn.onclick = ()=>{

            const userId =
            btn.dataset.id;

            if(

                Number(userId)

                ===

                Number(CURRENT_USER_ID)
            ){

                return;
            }

            if(selectedUsers.has(userId)){

                selectedUsers.delete(
                    userId
                );

                btn.classList.remove(
                    "selected"
                );
            }

            else{

                selectedUsers.add(
                    userId
                );

                btn.classList.add(
                    "selected"
                );
            }
        };
    });

    /* =========================
       SEARCH USERS
    ========================= */

    panel.querySelector(
        ".chat-forward-search"
    ).addEventListener(

        "input",

        (e)=>{

            const value =

            e.target.value
            .toLowerCase();

            panel.querySelectorAll(
                ".chat-forward-user"
            ).forEach(user=>{

                const name =

                    (
                        user.dataset.name || ""
                    )
                    .toLowerCase();

                user.style.display =

                    name.includes(value)

                    ?

                    "flex"

                    :

                    "none";
            });
        }
    );

    /* =========================
       CLOSE
    ========================= */

    panel.querySelector(
        ".chat-forward-close"
    ).onclick = ()=>{

        panel.remove();
    };

    /* =========================
       SEND
    ========================= */

    panel.querySelector(
        ".chat-forward-send"
    ).onclick = async ()=>{

        if(selectedUsers.size === 0){

            return;
        }

        try{

            for(const userId of selectedUsers){

                const response =
                await fetch(

                    "/chat/forward-message",

                    {

                        method:"POST",

                        headers:{

                            "Content-Type":
                            "application/json",

                            "X-CSRFToken":
                            csrfToken
                        },

                        body:JSON.stringify({

                            receiver_id:
                            userId,

                            message:
                            messageText
                        })
                    }
                );

                if(!response.ok){

                    console.error(
                        "Forward failed:",
                        userId
                    );
                }
            }

            panel.remove();

            showChatToast(
                "Message forwarded"
            );

            await loadMessages();
        }

        catch(error){

            console.error(
                error
            );

            alert(
                "Forward failed"
            );
        }
    };
}

/* =========================
   FORWARD MESSAGE
========================= */

document.addEventListener(

    "click",

    (e)=>{

        const forwardBtn =

        e.target.closest(
            ".forward-message-btn"
        );

        if(!forwardBtn){

            return;
        }

        e.preventDefault();

        e.stopPropagation();

        const messageId =
        forwardBtn.dataset.id;

        const messageElement =

        document.querySelector(

            `.chat-message[data-message-id="${messageId}"]`
        );

        if(!messageElement){

            return;
        }

        const messageText =

            messageElement.querySelector(
                ".chat-message-text"
            )?.innerText || "";

        openForwardPanel(

            messageId,

            messageText
        );
    }
);


/* =========================
   DELETE MESSAGE
========================= */

document.addEventListener(

    "click",

    (e)=>{

        const deleteBtn =

        e.target.closest(
            ".delete-message-btn"
        );

        if(!deleteBtn){

            return;
        }

        e.preventDefault();

        e.stopPropagation();

        const messageId =
        deleteBtn.dataset.id;

        if(!messageId){

            return;
        }

        openDeletePopup(
            messageId
        );
    }
);


/* =========================
   CHAT MENU
========================= */

chatMenuBtn?.addEventListener(

    "click",

    (e)=>{

        e.stopPropagation();

        chatMenuDropdown?.classList.toggle(
            "active"
        );
    }
);


/* =========================
   PROFILE MODAL
========================= */

viewProfileBtn?.addEventListener(

    "click",

    async ()=>{

        if(!activeReceiverId){

            return;
        }

        try{

            const response =
            await fetch(

                `/chat/user/${activeReceiverId}`
            );

            if(!response.ok){

                return;
            }

            const user =
            await response.json();

            const modal =

            document.getElementById(
                "chatProfileModal"
            );

            if(!modal){

                return;
            }

            modal.classList.add(
                "active"
            );

            const avatar =
            document.getElementById(
                "chatProfileAvatar"
            );

            const banner =
            document.getElementById(
                "chatProfileBanner"
            );

            if(avatar){

                avatar.src =

                    user.profile_image ||

                    "/static/default-avatar.png";
            }

            if(banner){

                if(user.banner){

                    banner.src =
                    user.banner;

                    banner.style.display =
                    "block";
                }

                else{

                    banner.removeAttribute(
                        "src"
                    );

                    banner.style.display =
                    "none";
                }
            }

            const fullNameEl =
            document.getElementById(
                "chatProfileFullName"
            );

            if(fullNameEl){

                fullNameEl.innerText =
                user.full_name || "-";
            }

            const firstNameEl =
            document.getElementById(
                "chatProfileFirstName"
            );

            if(firstNameEl){

                firstNameEl.innerText =
                user.first_name || "-";
            }

            const lastNameEl =
            document.getElementById(
                "chatProfileLastName"
            );

            if(lastNameEl){

                lastNameEl.innerText =
                user.last_name || "-";
            }

            const emailEl =
            document.getElementById(
                "chatProfileEmail"
            );

            if(emailEl){

                emailEl.innerText =
                user.email || "-";
            }

            const employeeIdEl =
            document.getElementById(
                "chatProfileEmployeeId"
            );

            if(employeeIdEl){

                employeeIdEl.innerText =
                user.employee_id || "-";
            }

            const roleEl =
            document.getElementById(
                "chatProfileRole"
            );

            if(roleEl){

                roleEl.innerText =
                user.role || "-";
            }
        }

        catch(error){

            console.error(

                "PROFILE LOAD ERROR:",

                error
            );
        }
    }
);


/* =========================
   CLOSE PROFILE
========================= */

document.getElementById(
    "closeChatProfile"
)?.addEventListener(

    "click",

    ()=>{

        document.getElementById(
            "chatProfileModal"
        )?.classList.remove(
            "active"
        );
    }
);


/* =========================
   ESC CLOSE
========================= */

document.addEventListener(

    "keydown",

    (e)=>{

        if(e.key !== "Escape"){

            return;
        }

        document
        .querySelectorAll(
            ".chat-message-dropdown"
        )
        .forEach(drop=>{

            drop.classList.remove(
                "active"
            );
        });

        chatMenuDropdown?.classList.remove(
            "active"
        );

        document.getElementById(
            "chatProfileModal"
        )?.classList.remove(
            "active"
        );

        document.querySelector(
            ".chat-forward-panel"
        )?.remove();

        document.getElementById(
            "chatDeletePopup"
        )?.remove();
    }
);


/* =========================
   ESCAPE HTML
========================= */

function escapeHtml(text){

    const div =
    document.createElement(
        "div"
    );

    div.innerText =
    text || "";

    return div.innerHTML;
}


/* =========================
   AUTO SCROLL
========================= */

function scrollMessages(){

    requestAnimationFrame(

        ()=>{

            if(!chatMessages){

                return;
            }

            chatMessages.scrollTop =

                chatMessages.scrollHeight;
        }
    );
}


/* =========================
   MARK READ
========================= */

function markVisibleMessagesRead(){

    if(!socket.connected){

        return;
    }

    document
    .querySelectorAll(
        ".chat-message.other"
    )
    .forEach(message=>{

        const id =
        message.dataset.messageId;

        if(!id){

            return;
        }

        if(message.classList.contains("read")){

            return;
        }

        socket.emit(

            "mark_read",

            {
                message_id:id
            }
        );

        message.classList.add(
            "read"
        );
    });
}


/* =========================
   AUTO READ
========================= */

chatMessages?.addEventListener(

    "scroll",

    ()=>{

        if(readThrottle){

            return;
        }

        readThrottle = true;

        markVisibleMessagesRead();

        setTimeout(

            ()=>{

                readThrottle = false;

            },

            2500
        );
    }
);


/* =========================
   CLEAR CHAT
========================= */

window.clearCurrentChat = function(){

    if(!activeReceiverId){

        return;
    }

    const confirmed = confirm(
        "Clear this conversation?"
    );

    if(!confirmed){

        return;
    }

    socket.emit(

        "clear_chat",

        {
            receiver_id:
            activeReceiverId
        }
    );

    if(chatMessages){

        chatMessages.innerHTML = "";
    }
};


/* =========================
   ARCHIVE CHAT
========================= */

const archiveChatBtn =
document.getElementById(
    "archiveChatBtn"
);

archiveChatBtn?.addEventListener(

    "click",

    async ()=>{

        if(!activeReceiverId){

            return;
        }

        try{

            const response =
            await fetch(

                "/chat/archive",

                {

                    method:"POST",

                    headers:{

                        "Content-Type":
                        "application/json",

                        "X-CSRFToken":
                        csrfToken
                    },

                    body:JSON.stringify({

                        conversation_id:
                        activeReceiverId
                    })
                }
            );

            if(!response.ok){

                return;
            }

            chatConversation?.classList.remove(
                "active"
            );

            if(chatMessages){

                chatMessages.innerHTML = "";
            }

            activeReceiverId = null;

            showChatToast(
                "Chat archived"
            );
        }

        catch(error){

            console.error(
                error
            );
        }
    }
);



/* =========================
   CLEAR CHAT BTN
========================= */

const clearChatBtn =
document.getElementById(
    "clearChatBtn"
);

clearChatBtn?.addEventListener(

    "click",

    ()=>{

        clearCurrentChat();
    }
);


/* =========================
   ADD TO GROUP
========================= */

const addToGroupBtn =
document.getElementById(
    "addToGroupBtn"
);

addToGroupBtn?.addEventListener(

    "click",

    ()=>{

        console.log(
            "Add to group clicked"
        );

        showChatToast(
            "Group feature coming soon"
        );
    }
);


/* =========================
   SOCKET RECONNECT ERROR
========================= */

if(socket?.io){

    socket.io.on(

        "reconnect_error",

        (err)=>{

            console.error(

                "Reconnect error:",

                err
            );
        }
    );
}


/* =========================
   INITIAL ICONS
========================= */

if(

    window.lucide
    &&
    typeof lucide.createIcons === "function"
){

    lucide.createIcons();
}


/* =========================
   END INIT
========================= */

}
