"""
This is a FRU object class to keep track of the current FRU details that you're working with.
"""


class FRUDetails:

    def __init__(self):

        self.chassis_part_number = None
        self.chassis_serial_number = None
        self.pd_serial_number = None
        self.pd_asset_tag = None
        self.pd_custom_field2 = None
