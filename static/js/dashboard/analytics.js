const DashboardAnalytics = (function(){

    async function loadDashboard(){

        try{

            showLoadingState();

            const data =
            await ApiService.get(
                "/api/dashboard/analytics"
            );

            renderStats(data);

            renderRevenueChart(data);

            renderRecentActivity(data);

            hideLoadingState();

        }catch(error){

            console.error(
                "[DASHBOARD ERROR]",
                error
            );

            Toast.error(
                "Failed to load analytics"
            );

        }

    }

    function renderStats(data){

        updateElement(
            "#revenueValue",
            data.total_revenue
        );

        updateElement(
            "#usersValue",
            data.active_users
        );

        updateElement(
            "#conversionValue",
            data.conversion_rate
        );

        updateElement(
            "#growthValue",
            data.growth
        );

    }

    function renderRevenueChart(data){

        DashboardCharts
        .createRevenueChart({

            selector:"#revenueChart",

            categories:
            data.chart.labels,

            series:
            data.chart.values

        });

    }

    function renderRecentActivity(data){

        const tableBody =
        document.querySelector(
            "#activityTableBody"
        );

        if(!tableBody) return;

        tableBody.innerHTML =
        data.activities
        .map(activity=>`
            <tr>
                <td>${activity.name}</td>
                <td>${activity.status}</td>
            </tr>
        `)
        .join("");

    }

    function updateElement(
        selector,
        value
    ){

        const el =
        document.querySelector(selector);

        if(el){

            el.innerText = value;

        }

    }

    function showLoadingState(){

        document
        .querySelectorAll(
            ".loading-target"
        )
        .forEach(el=>{

            el.classList.add(
                "loading-skeleton"
            );

        });

    }

    function hideLoadingState(){

        document
        .querySelectorAll(
            ".loading-target"
        )
        .forEach(el=>{

            el.classList.remove(
                "loading-skeleton"
            );

        });

    }

    return {

        loadDashboard

    };

})();

document.addEventListener(
    "DOMContentLoaded",
    function(){

        if(
            document.body.dataset.dashboard
            === "true"
        ){

            DashboardAnalytics
            .loadDashboard();

        }

    }
);