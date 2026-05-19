const DashboardCharts = (function(){

    const chartInstances = {};

    function getThemeColors(){

        const styles =
        getComputedStyle(
            document.documentElement
        );

        return {

            primary:
            styles.getPropertyValue(
                "--accent-primary"
            ).trim(),

            secondary:
            styles.getPropertyValue(
                "--accent-blue"
            ).trim(),

            text:
            styles.getPropertyValue(
                "--text-secondary"
            ).trim(),

            border:
            "rgba(255,255,255,0.08)"

        };

    }

    function createRevenueChart({

        selector,
        categories,
        series

    }){

        const colors =
        getThemeColors();

        const options = {

            chart:{
                type:"area",
                height:340,
                toolbar:{
                    show:false
                },
                background:"transparent"
            },

            series:[{
                name:"Revenue",
                data:series
            }],

            xaxis:{
                categories,
                labels:{
                    style:{
                        colors:colors.text
                    }
                },
                axisBorder:{
                    show:false
                }
            },

            yaxis:{
                labels:{
                    style:{
                        colors:colors.text
                    }
                }
            },

            grid:{
                borderColor:
                colors.border
            },

            dataLabels:{
                enabled:false
            },

            stroke:{
                curve:"smooth",
                width:3
            },

            fill:{
                type:"gradient",
                gradient:{
                    shadeIntensity:1,
                    opacityFrom:0.35,
                    opacityTo:0.02
                }
            },

            tooltip:{
                theme:"dark"
            },

            colors:[
                colors.primary
            ],

            legend:{
                labels:{
                    colors:colors.text
                }
            }

        };

        const chart =
        new ApexCharts(
            document.querySelector(selector),
            options
        );

        chart.render();

        chartInstances[selector] =
        chart;

        return chart;

    }

    function destroyAllCharts(){

        Object.values(chartInstances)
        .forEach(chart=>{

            chart.destroy();

        });

    }

    return {

        createRevenueChart,
        destroyAllCharts

    };

})();