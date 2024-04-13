# import doctest
#
# """
# >>> sum_(10, 10)
# 20
# >>> sum_(10, -5)
# 5
# >>> sum_(-5, -5)
# -10
# >>> sum_(-5, 10)
# 5
# >>> sum_(-5, 'any string')
# Traceback (most recent call last):
#     ...
# TypeError: unsupported operand type(s) for +=: 'int' and 'str'
# """
#
#
# def sum_(*number):
#     n = 0
#     for numb in number:
#         n += numb
#     return n
#
# # sum_(123, 421341,231,312,31,234, 123,'bh')
# doctest.testmod(verbose=True)


from admin_task import api_operation

import json


ret_conf = api_operation.get_client('644_Infinite_Service', 'finland.ggkala.shop')
# client_list = json.loads(ret_conf['obj']['settings'])['clients']

print(ret_conf)