"""Module that is used for storing respons dicts"""


class MultiLevelObject(object):
    """
        Turn multi dimensional dictionary into an object of objects.
        Used to turn raw API data into an object.
    """
    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                if isinstance(data[x], list):
                    list_data = data[x]
                    obj_list = []
                    for index in range(len(list_data)):
                        obj_list.append(MultiLevelObject(list_data[index]))
                    setattr(self, x, obj_list)
                else:
                    obj = data[x]
                    setattr(self, x, obj)
