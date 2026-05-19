const WorkspaceSheets = (function(){

    let sheets = {};

    let activeSheet = null;

    function registerSheet({

        id,
        instance,
        saveUrl

    }){

        sheets[id] = {

            id,
            instance,
            saveUrl

        };

        if(!activeSheet){

            activeSheet = id;

        }

    }

    function setActiveSheet(id){

        if(!sheets[id]) return;

        activeSheet = id;

        window.dispatchEvent(
            new CustomEvent(
                "sheet:changed",
                {
                    detail:{ id }
                }
            )
        );

    }

    function getActiveSheet(){

        return sheets[activeSheet];
    }

    async function saveSheet(id){

        const sheet =
        sheets[id];

        if(!sheet) return;

        const data =
        sheet.instance.getData();

        return ApiService.post(
            sheet.saveUrl,
            {
                data
            }
        );

    }

    async function saveAllSheets(){

        const promises =
        Object.keys(sheets)
        .map(id=>saveSheet(id));

        return Promise.all(promises);

    }

    function initializeAutosave(){

        Object.keys(sheets)
        .forEach(id=>{

            const sheet =
            sheets[id];

            sheet.instance.addHook(
                "afterChange",
                function(changes,source){

                    if(
                        source === "loadData"
                    ) return;

                    AutosaveService.save({

                        key:`sheet-${id}`,

                        delay:1500,

                        saveFunction:
                        ()=>saveSheet(id)

                    });

                }
            );

        });

    }

    return {

        registerSheet,
        setActiveSheet,
        getActiveSheet,
        saveSheet,
        saveAllSheets,
        initializeAutosave

    };

})();