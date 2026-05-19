from flask import jsonify

from flask_login import login_required

from app.api.v1 import api_v1

from app.services.analytics_service import (
    AnalyticsService
)

from app.utils.responses import (
    success_response,
    error_response
)


@api_v1.route("/dashboard")
@login_required
def dashboard_analytics():

    try:

        analytics = (
            AnalyticsService
            .get_dashboard_metrics()
        )

        return success_response(
            data=analytics
        )

    except Exception as error:

        return error_response(
            message=str(error),
            status_code=500
        )