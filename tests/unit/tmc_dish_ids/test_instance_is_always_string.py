from ska_mid_itf_engineering_tools.tmc_config.tmc_dish_ids import *

def test_instance_is_always_string():
    assert instance("SKA008") == '008', "expected \'008\', instead received " + instance("SKA008") 
    