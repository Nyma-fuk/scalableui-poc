# Architecture Docs

ScalableUI と AAOS platform の責務分担を説明する資料。

| 文書 | 何が理解できるか | 何ができるようになるか |
| --- | --- | --- |
| [scalableui_window_manager_flow_ja.md](scalableui_window_manager_flow_ja.md) | app launch、ActivityTaskManager、WindowManager/Shell、TaskPanel、Panel 表示の流れ | 「Panel に app が表示される」実体を図で説明できる |
| [aaos_app_layer_scalableui_scope_ja.md](aaos_app_layer_scalableui_scope_ja.md) | app layer、RRO/XML、controller、task event の境界 | 個人検証で作るものと対象 AAOS 環境で取り込むものを分けて整理できる |
| [panel_reorder_interaction_design_ja.md](panel_reorder_interaction_design_ja.md) | 3 Panel の全面drag、編集モード、Spy window、Drop確定の設計比較 | Map操作を維持しながら固定3-slotのPanel swapを段階実装できる |
