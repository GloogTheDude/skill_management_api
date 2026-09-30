from controllers import employee_certification_controller, employee_diploma_controller


def _get_paths(router):
    return [route.path for route in router.routes if "GET" in route.methods]


def test_employee_diploma_collection_route_precedes_dynamic_route():
    paths = _get_paths(employee_diploma_controller.router)
    assert paths.index("/employee_diploma/employee/{id_employee}") < paths.index(
        "/employee_diploma/{id_employee}/{id_diploma}"
    )


def test_employee_certification_collection_route_precedes_dynamic_route():
    paths = _get_paths(employee_certification_controller.router)
    assert paths.index("/employee_certification/employee/{id_employee}") < paths.index(
        "/employee_certification/{id_employee_certification}"
    )
