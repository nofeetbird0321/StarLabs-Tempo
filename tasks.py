# Main task list - defines which tasks will be executed / 主任务列表 - 定义将执行哪些任务
TASKS = ["FAUCET"]

# Individual task definitions / 单个任务定义
FAUCET = ["faucet"]  # Claim tokens from faucet / 从水龙头领取代币
TOKEN_SENDER = ["token_sender"]  # Send tokens to addresses / 发送代币到地址
DEX_SWAPS = ["dex_swaps"]  # Perform DEX token swaps / 执行DEX代币交换
ONCHAINGM_GM = ["onchaingm_gm"]  # OnchainGM GM task / OnchainGM GM任务
ONCHAINGM_DEPLOY = ["onchaingm_deploy"]  # Deploy OnchainGM contract / 部署OnchainGM合约
INFINITYNAME_DOMAIN = ["infinityname_domain"]  # Mint InfinityName domain / 铸造InfinityName域名
"""
EN:
You can create your own task with the modules you need 
and add it to the TASKS list or use our ready-made preset tasks.

( ) - Means that all of the modules inside the brackets will be executed 
in random order
[ ] - Means that only one of the modules inside the brackets will be executed 
on random
SEE THE EXAMPLE BELOW:

RU:
Вы можете создать свою задачу с модулями, которые вам нужны, 
и добавить ее в список TASKS, см. пример ниже:

( ) - означает, что все модули внутри скобок будут выполнены в случайном порядке
[ ] - означает, что будет выполнен только один из модулей внутри скобок в случайном порядке
СМОТРИТЕ ПРИМЕР НИЖЕ:

CHINESE:
你可以创建自己的任务，使用你需要的模块，
并将其添加到TASKS列表中，请参见下面的示例：

( ) - 表示括号内的所有模块将按随机顺序执行
[ ] - 表示括号内的模块将按随机顺序执行

--------------------------------
!!! IMPORTANT !!!
EXAMPLE | ПРИМЕР | 示例:

TASKS = [
    "CREATE_YOUR_OWN_TASK",
]
CREATE_YOUR_OWN_TASK = [
    "faucet",
    ("faucet_tokens", "swaps"),
    ["storagescan_deploy", "conft_mint"],
    "swaps",
]
--------------------------------


BELOW ARE THE READY-MADE TASKS THAT YOU CAN USE:
СНИЗУ ПРИВЕДЕНЫ ГОТОВЫЕ ПРИМЕРЫ ЗАДАЧ, КОТОРЫЕ ВЫ МОЖЕТЕ ИСПОЛЬЗОВАТЬ:
以下是您可以使用的现成任务：
"""
