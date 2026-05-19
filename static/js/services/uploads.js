const UploadService = (function(){

    async function uploadFiles({

        url,
        files,
        fieldName = "files",
        extraData = {},
        onSuccess,
        onError

    }){

        try{

            if(!files || !files.length){

                Toast.warning(
                    "No files selected"
                );

                return;
            }

            const formData =
            new FormData();

            Array.from(files).forEach(file=>{

                formData.append(
                    fieldName,
                    file
                );

            });

            Object.entries(extraData)
            .forEach(([key,value])=>{

                formData.append(
                    key,
                    value
                );

            });

            const response =
            await fetch(url,{
                method:"POST",
                body:formData
            });

            const data =
            await response.json();

            if(!response.ok){

                throw data;
            }

            Toast.success(
                data.message ||
                "Upload completed"
            );

            if(onSuccess){

                onSuccess(data);

            }

            return data;

        }catch(error){

            console.error(
                "[UPLOAD ERROR]",
                error
            );

            Toast.error(
                error.message ||
                "Upload failed"
            );

            if(onError){

                onError(error);

            }

            throw error;

        }

    }

    return {

        uploadFiles

    };

})();