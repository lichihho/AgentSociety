# Agent Block 客製化設計

在 `agentsociety` 框架中，`Agent` 的行為是透過一系列可組合的 `Block` 來定義的。這種模組化設計允許開發者彈性地客製化和擴充 `Agent` 的功能。`Block` 是 `Agent` 認知架構中的核心建構單元，負責處理特定的任務或行為邏輯。

## 核心概念

1.  **Block 基礎類別**:
    所有客製化的 `Block` 都必須繼承自 `agentsociety.agent.block.Block` 這個抽象基礎類別。這個類別定義了 `Block` 的基本介面和生命週期方法。

2.  **Agent 基礎類別**:
    `Agent` 的核心邏輯由 `agentsociety.agent.agent_base.Agent` 類別定義。`Agent` 在初始化時可以接收一個 `blocks` 列表，這些 `Block` 將會在 `Agent` 的執行週期中被調用。

3.  **生命週期與執行流程**:
    `Agent` 的主要執行方法是 `forward()`。在 `forward()` 方法中，會依序執行 `before_blocks()`、所有 `Block` 的 `forward()`，以及 `after_blocks()`。這使得開發者可以在 `Block` 執行前後注入自訂邏輯。

## 客製化步驟

要設計一個客製化的 `Agent Block`，主要需要完成以下步驟：

1.  **定義 `Block` 類別**：
    建立一個新的 Python 類別，並繼承自 `agentsociety.agent.block.Block`。

    ```python
    from agentsociety.agent.block import Block, BlockOutput
    from agentsociety.agent.context import DotDict

    class CustomLogicBlock(Block):
        """
        一個處理特定商業邏輯的客製化 Block。
        """
        ...
    ```

2.  **實作 `forward` 方法**：
    這是 `Block` 的核心執行邏輯。您必須覆寫 (override) `forward` 方法。此方法接收一個 `agent_context` 物件，您可以在此定義 `Block` 的主要行為。

    ```python
    async def forward(self, agent_context: DotDict) -> BlockOutput:
        """
        執行客製化邏輯。

        :param agent_context: Agent 的上下文，包含當前狀態和資訊。
        :return: Block 的輸出。
        """
        # 存取 Agent 的記憶體或狀態
        current_location = await self.agent_memory.get("current_location")
        
        # 使用大型語言模型 (LLM) 進行決策
        prompt = f"Based on being at {current_location}, what should be the next action?"
        response = await self.llm.atext_request(prompt)

        # 更新 Agent 的上下文或狀態
        agent_context.update({"next_action": response})
        
        # 返回 BlockOutput
        return BlockOutput(success=True, consumed_time=10)

    ```

3.  **定義參數與上下文 (可選)**：
    如果您的 `Block` 需要可配置的參數或特定的上下文結構，您可以定義 `ParamsType` 和 `ContextType`。

    ```python
    from agentsociety.agent.block import BlockParams, BlockContext

    class CustomBlockParams(BlockParams):
        threshold: float = 0.5
        mode: str = "default"

    class CustomBlockContext(BlockContext):
        processed_items: int = 0

    class CustomLogicBlock(Block):
        ParamsType = CustomBlockParams
        ContextType = CustomBlockContext
        ...
    ```

4.  **整合至 `Agent`**：
    在建立 `Agent` 實例時，將您客製化的 `Block` 加入到 `blocks` 列表中。

    ```python
    from agentsociety.agent.agent import CitizenAgentBase
    from agentsociety.agent.toolbox import AgentToolbox
    from agentsociety.memory.memory import Memory

    # 假設 toolbox 和 memory 已經被初始化
    toolbox = ... 
    memory = ...

    custom_block = CustomLogicBlock(toolbox=toolbox, agent_memory=memory)

    agent = CitizenAgentBase(
        id=1,
        name="CustomCitizen",
        toolbox=toolbox,
        memory=memory,
        blocks=[custom_block]
    )
    ```

### Block 的功能與特性

*   **存取工具箱 (`Toolbox`)**: 透過 `self.toolbox`，`Block` 可以存取如 `LLM`、`Environment` 等核心工具。
*   **記憶體管理**: `Block` 可以透過 `self.agent_memory` 和 `self.block_memory` 存取 `Agent` 層級和 `Block` 自身層級的記憶體。
*   **非同步支援**: `forward` 方法被設計為非同步 (`async`)，允許進行高效能的 I/O 操作。

### 結論

`Agent Block` 的設計提供了一個強大且靈活的機制來建構複雜的 `Agent` 行為。透過繼承 `Block` 基礎類別並實現 `forward` 方法，開發者可以將複雜的邏輯封裝成可重用、可組合的單元，從而實現高度客製化的 `Agent` 設計。這種模組化的方法不僅提升了程式碼的可維護性，也促進了不同 `Agent` 功能模組的共享與重用。