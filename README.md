<!--
 * @Date: 2020-10-20 12:12:03
 * @LastEditors: Dash Zhou
 * @LastEditTime: 2020-10-20 12:25:12
-->
## 基于python-can的can_player，加入模拟XCU UDP协议的interface实现了回放asclog并通过UDP发送的功能；

## setup environment
```shell
cd python-can
export PYTHONPATH=${PWD}
```

## run can_player

```shell
cd scripts
python3 ./can_player.py -i xcudp ../test/data/test_CanMessage.asc
```
