from features.steps.deciders import ArgonautObservationDecider
from tests.testvitals import VitalsResource
from features.steps.argonaut import found_at_least_one, vital_unit_validation
import copy
import pytest


def test_argonaut_validation():
    resources = VitalsResource().get_resources()

    assert ArgonautObservationDecider(resources[0]).should_validate()
    assert not ArgonautObservationDecider(resources[1]).should_validate()


def test_found_one():
    resources = VitalsResource().get_resources()

    resource_path = "Observation.category.coding.code".split(".")
    resource_path.pop(0)

    fake_resource = resources[0]

    assert found_at_least_one([fake_resource], resource_path, "vital-signs")

    fake_resource["category"]["coding"][0]["code"] = "not-vital-signs"

    assert not found_at_least_one([fake_resource], resource_path, "vital-signs")


@pytest.mark.skip(reason="Bloom Filter is out of date, will fix.")
def test_ucum_validation():
    resources = VitalsResource().get_resources()

    resource_path = "Observation.category.coding.code".split(".")
    resource_path.pop(0)

    wrong_system_response = {'resource': "", 'status': 'Wrong System'}
    wrong_code_response = {'resource': "", 'status': 'Invalid Code'}
    mismatch_code_response = {'resource': "", 'status': 'Mismatched vital unit and vital type'}

    wrong_system_response_bp = {'resource': "", 'status': 'Wrong System'}
    wrong_code_response_bp = {'resource': "", 'status': 'Invalid Code'}
    mismatch_code_response_bp = {'resource': "", 'status': 'Mismatched vital unit and vital type'}

    system_url = "http://unitsofmeasure.org"

    value_path = "Observation.valueQuantity"
    component_value_path = "Observation.component.valueQuantity"

    # Correct valueQuantity
    fake_resource = copy.deepcopy(resources[0])
    assert vital_unit_validation(value_path, fake_resource, system_url) is None

    # Bad system valueQuantity
    fake_resource["valueQuantity"]["system"] = "http://notunitsofmeasure.org"
    wrong_system_response["resource"] = fake_resource
    assert vital_unit_validation(value_path, fake_resource, system_url) == wrong_system_response

    # Bad code valueQuantity
    fake_resource = copy.deepcopy(resources[0])
    fake_resource["valueQuantity"]["code"] = "kgg"
    wrong_code_response["resource"] = fake_resource
    assert vital_unit_validation(value_path, fake_resource, system_url) == wrong_code_response

    # Mismatched valueQuantity
    fake_resource = copy.deepcopy(resources[0])
    fake_resource["valueQuantity"]["code"] = "/min"
    mismatch_code_response["resource"] = fake_resource
    assert vital_unit_validation(value_path, fake_resource, system_url) == mismatch_code_response

    # Correct component valueQuantity
    fake_resource = copy.deepcopy(resources[2])
    assert vital_unit_validation(component_value_path, fake_resource, system_url) is None

    # Bad component system valueQuantity
    fake_resource["component"][0]["valueQuantity"]["system"] = "http://notunitsofmeasure.org"
    wrong_system_response_bp["resource"] = fake_resource
    assert vital_unit_validation(component_value_path, fake_resource, system_url) \
        == wrong_system_response_bp

    # Bad component code valueQuantity
    fake_resource = copy.deepcopy(resources[2])
    fake_resource["component"][0]["valueQuantity"]["code"] = "kgg"
    wrong_code_response_bp["resource"] = fake_resource
    assert vital_unit_validation(component_value_path, fake_resource, system_url) \
        == wrong_code_response_bp

    # Mismatched component valueQuantity
    fake_resource = copy.deepcopy(resources[2])
    fake_resource["component"][0]["valueQuantity"]["code"] = "/min"
    mismatch_code_response_bp["resource"] = fake_resource
    assert vital_unit_validation(component_value_path, fake_resource, system_url) \
        == mismatch_code_response_bp
