"""hermes-zh：控制台中文增强。

全部功能在网页控制台的 ``dashboard/dist/index.js``（运行时词典），
Python 侧不注册工具、钩子或命令，只需要一个 register() 让宿主把插件视为已加载。
"""


def register(ctx):  # noqa: ARG001 - 宿主会传入 PluginContext，这里不需要
    """空实现：本插件不向 agent 注册任何能力。"""
    return None
