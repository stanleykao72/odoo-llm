# Odoo 18.0 視圖變化升級指南

## 目錄
1. [Tree View 改為 List View](#1-tree-view-改為-list-view)
2. [attrs 屬性的替代方案](#2-attrs-屬性的替代方案)
3. [Chatter 的簡化語法](#3-chatter-的簡化語法)
4. [其他重要變更](#4-其他重要變更)
5. [升級工具與技巧](#5-升級工具與技巧)
6. [JavaScript (static/src) 18.0 升級指南](#6-javascript-staticsrc-180-升級指南)

---

## 1. Tree View 改為 List View

### 變更說明
在 Odoo 18.0 中，列表視圖的根元素從 `<tree>` 改為 `<list>`。這是一個重大但簡單的變更。

### 升級範例

**Odoo 17 及之前版本：**
```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Model List" create="true" delete="true" editable="bottom">
            <field name="name"/>
            <field name="date"/>
            <field name="amount"/>
        </tree>
    </field>
</record>
```

**Odoo 18.0：**
```xml
<record id="view_my_model_list" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Model List" create="true" delete="true" editable="bottom">
            <field name="name"/>
            <field name="date"/>
            <field name="amount"/>
        </list>
    </field>
</record>
```

### 注意事項
- 確保所有屬性（如 `create`、`delete`、`editable`、`default_order`）都在 `<list>` 標籤內部
- 升級腳本可能會錯誤地將這些屬性放在標籤外部，導致 XML 格式錯誤

---

## 2. attrs 屬性的替代方案

### 變更說明
從 Odoo 17 開始，`attrs` 和 `states` 屬性不再使用。Odoo 18 使用直接屬性來取代嵌套的字典結構。

### 2.1 invisible 屬性

**舊版寫法：**
```xml
<field name="department_id" attrs="{'invisible': [('state', '=', 'done')]}"/>
<field name="type" attrs="{'invisible': ['|', ('state', '=', 'done'), ('type', '=', 'internal')]}"/>
```

**Odoo 18.0 寫法：**
```xml
<!-- 簡單條件 -->
<field name="department_id" invisible="state == 'done'"/>

<!-- 使用 or 運算符 -->
<field name="type" invisible="state == 'done' or type == 'internal'"/>

<!-- 使用 and 運算符 -->
<field name="notes" invisible="state == 'new' and status == 'pending'"/>

<!-- 使用 in 運算符 -->
<field name="status" invisible="state not in ['done', 'cancel']"/>
```

### 2.2 readonly 屬性

**舊版寫法：**
```xml
<field name="job_position" attrs="{'readonly': [('state', '=', 'approved')]}"/>
<field name="salary" attrs="{'readonly': ['&', ('state', '=', 'approved'), ('user_id', '!=', uid)]}"/>
```

**Odoo 18.0 寫法：**
```xml
<!-- 簡單條件 -->
<field name="job_position" readonly="state == 'approved'"/>

<!-- 複合條件 -->
<field name="salary" readonly="state == 'approved' and user_id != uid"/>

<!-- 使用 in 運算符 -->
<field name="description" readonly="state in ['ready', 'waiting', 'done']"/>
```

### 2.3 required 屬性

**舊版寫法：**
```xml
<field name="partner_id" attrs="{'required': [('type', '=', 'customer')]}"/>
```

**Odoo 18.0 寫法：**
```xml
<field name="partner_id" required="type == 'customer'"/>
<field name="vat" required="is_company == True"/>
```

### 2.4 組合多個屬性

**舊版寫法：**
```xml
<field name="name" attrs="{
    'invisible': [('condition1', '=', False)], 
    'required': [('condition2', '=', True)],
    'readonly': [('state', '=', 'confirmed')]
}"/>
```

**Odoo 18.0 寫法：**
```xml
<field name="name" 
       invisible="condition1 == False" 
       required="condition2 == True"
       readonly="state == 'confirmed'"/>
```

### 2.5 domain 屬性

**舊版寫法：**
```xml
<field name="partner_id" attrs="{'domain': [('is_company', '=', True)]}"/>
```

**Odoo 18.0 寫法：**
```xml
<field name="partner_id" domain="[('is_company', '=', True)]"/>
```

### 2.6 column_invisible 屬性

在 Odoo 17 開始，列表視圖中的 `invisible` 屬性只會隱藏單元格，不會隱藏整列。要隱藏整列，使用 `column_invisible`：

```xml
<list>
    <!-- 只隱藏特定行的單元格 -->
    <field name="internal_notes" invisible="is_public == True"/>
    
    <!-- 隱藏整個列 -->
    <field name="secret_field" column_invisible="True"/>
</list>
```

---

## 3. Chatter 的簡化語法

### 變更說明
Odoo 18 簡化了 chatter（聊天記錄）的實現方式，不再需要冗長的 XML 代碼。

### 3.1 標準 Chatter 實現

**簡化的 Chatter 定義：**
```xml
<form>
    <sheet>
        <!-- 表單內容 -->
        <group>
            <field name="name"/>
            <field name="partner_id"/>
        </group>
    </sheet>
    <!-- 簡化的 chatter -->
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

### 3.2 自定義 Chatter 選項

```xml
<div class="oe_chatter">
    <field name="message_follower_ids" groups="base.group_user"/>
    <field name="activity_ids"/>
    <field name="message_ids" options="{
        'display_log_button': True,
        'post_refresh': 'always',
        'open_attachments': True
    }"/>
</div>
```

### 3.3 前提條件

模型必須繼承 `mail.thread` mixin：

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'My Model'
    
    name = fields.Char('Name', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
```

---

## 4. 其他重要變更

### 4.1 Python 欄位定義中的 states 屬性移除

**Odoo 17 及之前：**
```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done')
], default='draft')

name = fields.Char('Name', states={
    'done': [('readonly', True)],
    'confirmed': [('required', True)]
})
```

**Odoo 18.0：**
```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done')
], default='draft')

name = fields.Char('Name')
# 狀態相關的邏輯現在在視圖 XML 中處理
```

### 4.2 視圖繼承的變化

確保繼承視圖時使用正確的標籤名稱：

```xml
<record id="view_inherit_my_model_list" model="ir.ui.view">
    <field name="name">my.model.list.inherit</field>
    <field name="model">my.model</field>
    <field name="inherit_id" ref="base_module.view_my_model_list"/>
    <field name="arch" type="xml">
        <xpath expr="//list" position="attributes">
            <attribute name="create">false</attribute>
        </xpath>
        <xpath expr="//field[@name='name']" position="after">
            <field name="new_field"/>
        </xpath>
    </field>
</record>
```

---

## 5. 升級工具與技巧

### 5.1 自動升級命令

使用 Odoo 的升級工具：

```bash
# 升級自定義模組代碼
./odoo-bin upgrade_code --from 17.0 --to 18.0 --addons-path /path/to/your/custom/modules
```

### 5.2 手動升級檢查清單

1. **替換所有 `<tree>` 標籤為 `<list>`**
   ```bash
   # 在你的模組目錄中查找所有需要更改的文件
   grep -r "<tree\|</tree>" . --include="*.xml"
   ```

2. **轉換所有 attrs 屬性**
   ```bash
   # 查找所有使用 attrs 的地方
   grep -r "attrs=" . --include="*.xml"
   ```

3. **更新 Python 文件中的 states 屬性**
   ```bash
   # 查找使用 states 的欄位定義
   grep -r "states=" . --include="*.py"
   ```

### 5.3 使用自動轉換工具

可以使用社群提供的工具來自動轉換 attrs：
- GitHub: https://github.com/pierrelocus/odoo-attrs-replace

### 5.4 測試建議

1. **建立測試資料庫**
   ```bash
   createdb odoo18_test
   ```

2. **逐個模組測試**
   ```bash
   ./odoo-bin -d odoo18_test -i your_module --stop-after-init
   ```

3. **檢查錯誤日誌**
   特別注意 XML 解析錯誤和視圖載入錯誤

### 5.5 常見問題解決

1. **XML 格式錯誤**
   - 確保所有屬性都在正確的標籤內
   - 檢查引號的使用（使用雙引號）

2. **條件表達式錯誤**
   - 使用 Python 風格的表達式（`==`, `!=`, `and`, `or`）
   - 避免使用舊的 domain 語法

3. **視圖無法載入**
   - 檢查繼承鏈是否正確
   - 確認父視圖已經更新為新格式

---

## 6. JavaScript (static/src) 18.0 升級指南

### 6.1 模組聲明變更

#### 變更說明
Odoo 18.0 仍然需要 `/** @odoo-module */` 聲明，但語法要求更嚴格。

#### 升級範例

**Odoo 16.0/17.0：**
```javascript
// 某些文件可能缺少模組聲明或格式不正確
import { Component } from "@odoo/owl";
```

**Odoo 18.0：**
```javascript
/** @odoo-module */

import { Component } from "@odoo/owl";
```

### 6.2 OWL 框架導入變更

#### 變更說明
OWL 組件的導入方式需要使用 ES6 import 語法，不再使用全域 owl 物件。

#### 升級範例

**Odoo 16.0 舊寫法：**
```javascript
const { Component } = owl;
const { useState, useRef, onMounted, onWillUnmount } = owl;

export class MyComponent extends Component {
    // 組件內容
}
```

**Odoo 18.0 新寫法：**
```javascript
/** @odoo-module */

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";

export class MyComponent extends Component {
    // 組件內容
}
```

### 6.3 組件屬性定義變更

#### 變更說明
組件屬性定義從 `Object.assign` 改為直接屬性賦值。

#### 升級範例

**Odoo 16.0 舊寫法：**
```javascript
export class LLMChatSidebar extends Component {
    // 組件內容
}

Object.assign(LLMChatSidebar, {
    props: { record: Object },
    template: "llm_thread.LLMChatSidebar",
    components: { SubComponent },
});
```

**Odoo 18.0 新寫法：**
```javascript
/** @odoo-module */

import { Component } from "@odoo/owl";

export class LLMChatSidebar extends Component {
    // 組件內容
}

LLMChatSidebar.props = { record: Object };
LLMChatSidebar.template = "llm_thread.LLMChatSidebar";
LLMChatSidebar.components = { SubComponent };
```

### 6.4 複雜組件升級範例

#### 多個 OWL 功能的組件

**Odoo 16.0 舊寫法：**
```javascript
import { registerMessagingComponent } from "@mail/utils/messaging_component";
import { useModels } from "@mail/component_hooks/use_models";
const { Component, useState, useRef, onMounted } = owl;

export class LLMChatThreadHeader extends Component {
    setup() {
        useModels();
        this.state = useState({
            isEditing: false,
        });
        this.titleRef = useRef("titleInput");
        
        onMounted(() => {
            this._setupComponent();
        });
    }
}

Object.assign(LLMChatThreadHeader, {
    props: { 
        record: Object,
        threadView: Object 
    },
    template: "llm_thread.LLMChatThreadHeader",
});
```

**Odoo 18.0 新寫法：**
```javascript
/** @odoo-module */

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registerMessagingComponent } from "@mail/utils/messaging_component";
import { useModels } from "@mail/component_hooks/use_models";

export class LLMChatThreadHeader extends Component {
    setup() {
        useModels();
        this.state = useState({
            isEditing: false,
        });
        this.titleRef = useRef("titleInput");
        
        onMounted(() => {
            this._setupComponent();
        });
    }
}

LLMChatThreadHeader.props = { 
    record: Object,
    threadView: Object 
};
LLMChatThreadHeader.template = "llm_thread.LLMChatThreadHeader";
```

### 6.5 Client Action 註冊升級

#### Client Action 文件結構

**Odoo 16.0 舊寫法：**
```javascript
import { LLMChatContainer } from "@llm_thread/components/llm_chat_container/llm_chat_container";
import { registry } from "@web/core/registry";

// 可能缺少模組聲明
registry
  .category("actions")
  .add("llm_thread.chat_client_action", LLMChatContainer);
```

**Odoo 18.0 新寫法：**
```javascript
/** @odoo-module */

import { LLMChatContainer } from "@llm_thread/components/llm_chat_container/llm_chat_container";
import { registry } from "@web/core/registry";

// Register the client action
registry
  .category("actions")
  .add("llm_thread.chat_client_action", LLMChatContainer);
```

### 6.6 模型文件升級

#### 模型導入文件

**所有模型導入文件需要添加模組聲明：**

```javascript
/** @odoo-module */

// Import all models to ensure they are registered
import "@llm_thread/models/llm_chat";
import "@llm_thread/models/llm_chat_view";
import "@llm_thread/models/messaging";
// ... 其他導入
```

### 6.7 批量升級腳本

#### 自動化升級流程

**1. 找出需要升級的 JavaScript 文件：**
```bash
# 找出缺少 @odoo-module 聲明的文件
find ./static/src -name "*.js" -exec grep -L "/** @odoo-module */" {} \;

# 找出使用舊 OWL 語法的文件
find ./static/src -name "*.js" -exec grep -l "const { Component } = owl" {} \;

# 找出使用 Object.assign 的組件定義
find ./static/src -name "*.js" -exec grep -l "Object.assign.*template\|Object.assign.*props" {} \;
```

**2. 批量修復腳本範例：**
```bash
#!/bin/bash

# 為所有 JavaScript 文件添加 @odoo-module 聲明
for file in $(find ./static/src -name "*.js" -exec grep -L "/** @odoo-module */" {} \;); do
    sed -i '1i/** @odoo-module */\n' "$file"
done

# 替換 OWL 導入語法
find ./static/src -name "*.js" -exec sed -i 's/const { Component } = owl;/import { Component } from "@odoo\/owl";/g' {} \;
find ./static/src -name "*.js" -exec sed -i 's/const { Component, useState } = owl;/import { Component, useState } from "@odoo\/owl";/g' {} \;

# 需要手動處理 Object.assign 轉換（較為複雜）
```

### 6.8 測試與驗證

#### JavaScript 語法驗證

**1. 檢查模組聲明：**
```bash
# 確保所有 JS 文件都有 @odoo-module 聲明
find ./static/src -name "*.js" -exec grep -L "/** @odoo-module */" {} \; | wc -l
# 應該回傳 0
```

**2. 檢查 OWL 導入：**
```bash
# 確保沒有舊的 OWL 語法
find ./static/src -name "*.js" -exec grep -l "const.*owl" {} \;
# 應該沒有結果
```

**3. 安裝測試：**
```bash
# 在 Odoo 18.0 環境中測試模組安裝
docker compose -f docker-compose.18.yml exec odoo18 \
  /usr/bin/odoo -c /etc/odoo/odoo.conf \
  --db_host=db18 --db_user=odoo --db_password=odoo \
  -d odoo -i llm_thread --stop-after-init
```

### 6.9 常見問題與解決方案

#### 問題 1: Client Action 註冊失敗
**錯誤：** `Cannot find key 'llm_thread.chat_client_action' in the 'actions' registry`

**解決方案：**
- 確保 client action 文件有 `/** @odoo-module */` 聲明
- 檢查導入路徑是否正確
- 驗證組件是否正確匯出

#### 問題 2: 組件載入失敗
**錯誤：** Component 相關的 JavaScript 錯誤

**解決方案：**
- 檢查所有 OWL 導入是否使用新語法
- 確保組件屬性使用直接賦值而非 Object.assign
- 驗證所有依賴組件也已正確升級

#### 問題 3: 模組依賴問題
**錯誤：** 模組載入順序或依賴問題

**解決方案：**
- 確保 main.js 文件正確導入所有必要模組
- 檢查 __manifest__.py 中的 assets 順序
- 驗證跨模組導入路徑

### 6.10 最佳實踐建議

#### 升級順序
1. **先升級基礎組件**（不依賴其他自定義組件的）
2. **再升級複合組件**（使用基礎組件的）
3. **最後升級 client actions**（註冊和使用組件的）

#### 代碼風格
- 保持一致的導入順序（Odoo 框架 → 第三方 → 本地）
- 使用明確的導入（避免 `import *`）
- 保持組件屬性定義的一致性

#### 測試策略
- 每修改一個文件就測試一次
- 使用瀏覽器開發者工具檢查 JavaScript 錯誤
- 確保所有功能在升級後正常運作

---

## 總結

Odoo 18.0 的升級包含視圖系統和 JavaScript 框架的重大變更：

### 視圖系統升級
1. **更直觀的語法**：直接使用屬性而非嵌套字典
2. **更好的可讀性**：條件表達式更接近 Python 語法
3. **減少樣板代碼**：特別是在 chatter 實現上

### JavaScript 框架升級
1. **嚴格的模組聲明**：所有 JS 文件必須包含 `/** @odoo-module */`
2. **現代化的 OWL 導入**：使用 ES6 import 語法取代全域物件
3. **簡化的組件定義**：直接屬性賦值取代 Object.assign

### 升級檢查清單
升級時務必：
- ✅ 完整測試所有視圖（XML）
- ✅ 驗證所有 JavaScript 組件正常載入
- ✅ 檢查 Client Actions 註冊成功
- ✅ 確保自定義邏輯正常運作
- ✅ 驗證所有使用者介面行為與預期一致

### 關鍵成功因素
1. **系統化的升級方法**：按照模組 → 組件 → 動作的順序升級
2. **充分的測試**：每個變更都要立即測試
3. **詳細的文檔記錄**：記錄所有變更以便後續維護

這些變更雖然需要一些工作來適應，但長期來看會讓代碼更易維護、更符合現代 JavaScript 標準，並提供更好的開發體驗。特別是 JavaScript 部分的升級，為未來的功能擴展和性能優化奠定了良好的基礎。