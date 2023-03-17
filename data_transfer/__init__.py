# Module that allows data transfer between two dictionaries of different
# layout, here specifically developed to transfer the input values from a
# GUI saved in a dictionary to an input dictionary for a simulation
try:
    import numpy as np
    NUMPY_FOUND = True
except ModuleNotFoundError:
    NUMPY_FOUND = False
from typing import Generator
import copy


def ensure_list(variable, length=1):
    """
    Ensures that the provided variable is a list, even if it contains only
    one element.

    :param variable: any type of variable, not manipulated if already list,
        tuple, or numpy array
    :param length: Length of repetitive entries in list of variable. Default
        is 1
    :return: List with length of parameter 'length' containing the provided
        'variable', only modified if 'variable' not already iterable
    """
    iterable_list = (list, tuple, np.ndarray) if NUMPY_FOUND \
        else (list, tuple)
    if isinstance(variable, iterable_list):
        return variable
    else:
        return [variable for i in range(length)]


def remove_key(key: str, var: (dict, list, tuple)) -> (dict, list, tuple):
    """
    A function that removes all entries with 'key' in nested dictionary or a
    list of nested dictionaries.

    :param key: the key specifying the entries to remove.
    :param var: the dictionary or list of dictionaries to remove entries from.

    Example usage:
    ```
    data = {'a': 1, 'b': {'c': 2, 'd': {'c': 3}}}
    results = remove_key('c', data)
    print(results) # {'a': 1, 'b': {'d': ''}}
    ```
    """
    if isinstance(var, dict):
        for k in list(var.keys()):
            if k == key:
                del var[key]
            else:
                remove_key(key, var[k])
    elif isinstance(var, (list, tuple)):
        for item in var:
            remove_key(key, item)


def gen_dict_extract(key: str, var: (dict, list, tuple)) -> Generator:
    """
    A generator function that extracts all nested dictionaries in a dictionary
    or a list of dictionaries that have a specific key.

    :param key: the key to search for in the dictionaries.
    :param var: the dictionary or list of
                               dictionaries to search in.
    :return: A generator that yields all the nested dictionaries that contain
        the key.

    Example usage:
    ```
    data = {'a': 1, 'b': {'c': 2, 'd': {'c': 3}}}
    results = list(gen_dict_extract('c', data))
    print(results) # [{'c': 2}, {'c': 3}]
    ```
    """
    if isinstance(var, dict):
        for k, v in var.items():
            if k == key:
                yield var
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result
    elif isinstance(var, (list, tuple)):
        for d in var:
            for result in gen_dict_extract(key, d):
                yield result
    # else:
    #     raise TypeError('Provided data structure must be either dict, list, '
    #                     'or tuple')


def set_dict_entry(value, key_list: list, target_dict: dict,
                   mode: str = "moderate") -> dict:
    """
    The set_dict_entry function sets the value of a dictionary entry at a
    specified location. It takes a value, a list of keys that specify the
    location, and the target dictionary. By default, the function operates in
    "moderate" mode, where a message is printed if the specified key is not
    found and the key will be added to the dictionary. However, if the mode
    parameter is set to
    "strict", a NameError is
    raised instead.

    :param value: The value to be set
    :param key_list: A list of keys that specify the location where the value
        should be set
    :param target_dict: The dictionary in which the value should be set
    :param mode: The mode of operation, either "moderate" or "strict"
        (default is "moderate")
    :return: The modified target dictionary
    """
    if isinstance(target_dict, dict):
        sub_dict = target_dict
    else:
        raise TypeError
    for i in range(len(key_list) - 1):
        sub_dict = sub_dict[key_list[i]]

    if key_list[-1] in sub_dict:
        if hasattr(value, 'value'):
            pure_value = value.value
        else:
            pure_value = value
        sub_dict[key_list[-1]] = pure_value
        flag_found = True
    else:
        if mode == "strict":
            raise NameError(f'Key {key_list} was not found in settings.json')
        else:
            print(f'Key {key_list} was not found in settings.json')

    return target_dict


def get_dict_entry(key_list: (list, tuple), source_dict: dict):
    """
    Get a specific entry from a nested dictionary (source_dict) according to
    the given list of keys (key_list)

    :param key_list: list of keys to locate entry in a nested dictionary
                     ordered from highest to lowest hierarchy
    :param source_dict: dictionary to retrieve value from
    :return: retrieved value
    """
    if isinstance(source_dict, dict):
        sub_dict = source_dict
    else:
        raise TypeError
    for i in range(len(key_list) - 1):
        sub_dict = sub_dict[key_list[i]]
    return sub_dict[key_list[-1]]


def dict_transfer(source_dict: dict, target_dict: dict,
                  target_name_key="sim_name", value_key="value") -> object:
    """
    Transfer values from a dictionary of GUI elements to a dictionary of
    simulation inputs.

    This function takes a `source_dict` that contains GUI elements and their
    values, and a `target_dict` that contains simulation input variables and
    their default values. It extracts the values of GUI elements that have a
    'target_name_key' key, and sets the corresponding variables in the
    `target_dict`. The function returns the updated `target_dict`, as
    well as a list of lists of simulation variable names that were updated.

    The `source_dict` is expected to have the following structure:
    - It is a nested dictionary of GUI elements, where each element is
      identified by a unique key.
    - Each GUI element may have one or more sim_name keys, whose values are
      lists of strings that represent the "path" of keys (for nested
      dictionaries) of the corresponding variable in the simulation input
      dictionary, i.e. the target dictionary
    - Each GUI element may also have a "value" key, whose value is the current
      value of the element.

    The `target_dict` is expected to have the following structure:
    - It is a nested dictionary of simulation input variables, where each
      variable is identified by a list of strings that represents its name (
      i.e., a "path" of keys in the dictionary).
    - The values of the variables are their default values, which may be of
      any type.

    The returned dictionary is a copy of target_dict with the updated
    values from the source_dict. list of lists of simulation variable
    names has
    the following
    structure:
    - Each sublist represents a set of variables that were updated together,
      because they were associated with a GUI element that had multiple
      "sim_name" keys.
    - Each element of the sublist is a list of strings that represents the
      name of a variable.

    :param source_dict: A dictionary of GUI elements and their values.
    :param target_dict: A dictionary of simulation input variables and their
                        default values.
    :param target_name_key: A string indicating the key in the 'source_dict'
                     containing the list of names mapping to the
                     corresponding variable in the 'target_dict'
    :param value_key: A string indicating the key for the values in the
                      'source_dict' and the 'target_dict'
    :return: A tuple containing an updated copy of `target_dict`, and a list of
             lists of simulation variable names that were updated.
    """
    target_dict_copy = copy.deepcopy(target_dict)

    # get only widgets with sim_names
    name_lists = []
    extracted_gui_entries = list(gen_dict_extract(target_name_key, source_dict))
    if extracted_gui_entries:
        for gui_entry in extracted_gui_entries:
            sim_names = gui_entry[target_name_key]
            sim_names = ensure_list(sim_names)
            sub_dict = target_dict_copy

            if isinstance(sim_names[0], list):
                gui_values = ensure_list(gui_entry[value_key])

                # if len(sim_names) != len(gui_values):
                #     gui_values = [gui_values[0] for i in range(len(sim_names))]
                if len(sim_names) == len(gui_values):
                    multi_variable = True
                else:
                    multi_variable = False

                for i, sim_name_list in enumerate(sim_names):
                    if isinstance(sim_name_list[-1], list):
                        pure_name_list = sim_name_list[:-1]
                        name_lists.append(pure_name_list)
                        value_list = []
                        for j in sim_name_list[-1]:
                            try:
                                value = gui_values[j]
                            except IndexError:
                                value = gui_values[-1]
                            if hasattr(value, 'value'):
                                pure_value = value.value
                            else:
                                pure_value = value
                            value_list.append(pure_value)
                        sub_dict = \
                            set_dict_entry(value_list, pure_name_list,
                                           sub_dict)
                    else:
                        name_lists.append(sim_name_list)
                        gui_value = gui_values[i] if multi_variable \
                            else gui_values[0]
                        sub_dict = set_dict_entry(gui_value, sim_name_list,
                                                  sub_dict)

            else:
                name_lists.append(sim_names)
                if value_key in gui_entry:
                    sub_dict = \
                        set_dict_entry(gui_entry[value_key], sim_names,
                                       sub_dict, mode="strict")
    return target_dict_copy, name_lists