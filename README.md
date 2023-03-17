# data-transfer
Python module to transfer data between different data strucutures. At the 
moment its only functionality is to transfer data between two nested python 
dictionaries with different structures using the 'dict_transfer' function. 
For details on usage see docstring of the 'dict_transfer' function.

### Requirements

- Python

### Example:

Input: 
```python
import data_transfer

source_dict = \
    {'temperature': {'sim_name': 'ambient_temp', 'value': '25'}}
target_dict = {'ambient_temp': {'value': '20'}}
print(data_transfer.dict_transfer(source_dict, target_dict, 
                                  target_name_key='sim_name',
                                  value_key='value'))
```
Output: 
```python
    ({'ambient_temp': {'value': '25'}}, ['ambient_temp'])
```
