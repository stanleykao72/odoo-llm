# Odoo 18.0 視圖變化升級指南

## 目錄
1. [Tree View 改為 List View](#1-tree-view-改為-list-view)
2. [attrs 屬性的替代方案](#2-attrs-屬性的替代方案)
3. [Chatter 的簡化語法](#3-chatter-的簡化語法)
4. [其他重要變更](#4-其他重要變更)
5. [升級工具與技巧](#5-升級工具與技巧)

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

## 總結

Odoo 18.0 的視圖系統變更主要著重於簡化和現代化：

1. **更直觀的語法**：直接使用屬性而非嵌套字典
2. **更好的可讀性**：條件表達式更接近 Python 語法
3. **減少樣板代碼**：特別是在 chatter 實現上

升級時務必：
- 完整測試所有視圖
- 檢查自定義邏輯是否正常運作
- 確保所有使用者介面行為與預期一致

這些變更雖然需要一些工作來適應，但長期來看會讓代碼更易維護和理解。