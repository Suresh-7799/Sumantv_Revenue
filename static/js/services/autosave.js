const AutosaveService = (function(){

    const timers = {};

    const states = {};

    function setState(key,state){

        states[key] = state;

        window.dispatchEvent(
            new CustomEvent(
                "autosave:state",
                {
                    detail:{
                        key,
                        state
                    }
                }
            )
        );

    }

    async function save({

        key,
        delay = 1200,
        saveFunction

    }){

        clearTimeout(
            timers[key]
        );

        setState(
            key,
            "pending"
        );

        timers[key] = setTimeout(
            async function(){

                try{

                    await saveFunction();

                    setState(
                        key,
                        "saved"
                    );

                }catch(error){

                    console.error(
                        "[AUTOSAVE ERROR]",
                        error
                    );

                    setState(
                        key,
                        "error"
                    );

                    Toast.error(
                        "Autosave failed"
                    );

                }

            },
            delay
        );

    }

    return {

        save

    };

})();