class AnalyticsService:

    @staticmethod
    def get_dashboard_metrics():

        return {

            "total_revenue":
            "$48.2K",

            "active_users":
            "8,492",

            "conversion_rate":
            "18.6%",

            "growth":
            "+24%",

            "chart": {

                "labels": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May"
                ],

                "values": [
                    1200,
                    2200,
                    3100,
                    4200,
                    5200
                ]

            },

            "activities": [

                {
                    "name":
                    "Revenue updated",

                    "status":
                    "Completed"
                },

                {
                    "name":
                    "Workspace synced",

                    "status":
                    "Running"
                }

            ]

        }