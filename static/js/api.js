const ApiService = (function(){

    async function request(
        url,
        options = {}
    ){

        const config = {

            headers:{
                "Content-Type":
                "application/json",
                ...(options.headers || {})
            },

            ...options

        };

        try{

            const response =
            await fetch(
                url,
                config
            );

            const contentType =
            response.headers.get(
                "content-type"
            );

            let data;

            if(
                contentType &&
                contentType.includes(
                    "application/json"
                )
            ){

                data =
                await response.json();

            }else{

                data =
                await response.text();

            }

            if(!response.ok){

                throw {

                    status:
                    response.status,

                    data
                };

            }

            return data;

        }catch(error){

            console.error(
                "[API ERROR]",
                error
            );

            if(window.Toast){

                Toast.error(
                    "Something went wrong"
                );

            }

            throw error;

        }

    }

    return {

        get(url){

            return request(
                url,
                {
                    method:"GET"
                }
            );

        },

        post(url,data){

            return request(
                url,
                {
                    method:"POST",

                    body:
                    JSON.stringify(data)
                }
            );

        },

        put(url,data){

            return request(
                url,
                {
                    method:"PUT",

                    body:
                    JSON.stringify(data)
                }
            );

        },

        delete(url){

            return request(
                url,
                {
                    method:"DELETE"
                }
            );

        }

    };

})();