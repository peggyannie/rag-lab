在实际的 Node.js 项目中，我们通常使用 **Mongoose** 作为 MongoDB 的建模工具。它能通过代码清晰地表达“嵌入”和“引用”。

我们继续以你提供的**“广告配置”**项目为例，看看在代码层面如何落地。

---

## 1. 嵌入 (Embedding) 的代码实现

**场景：** 广告配置中的“展示规则”（如：投放平台、优先级）。这些信息通常随广告一起创建，且数据量固定。

### 定义 Schema

在 Mongoose 中，嵌入是通过**子文档 (Sub-documents)** 实现的：

JavaScript

```
const mongoose = require('mongoose');

// 定义子文档：广告展示规则
const RuleSchema = new mongoose.Schema({
    platform: [String], // ['iOS', 'Android']
    priority: Number,   // 排序权重
    isTest: Boolean     // 是否是测试环境
});

// 定义主文档：广告配置
const AdSchema = new mongoose.Schema({
    name: String,
    position: String,
    rules: RuleSchema, // 直接嵌入子文档对象
    // 或者嵌入子文档数组：items: [ItemSchema]
});

const Ad = mongoose.model('Ad', AdSchema);
```

### 操作方式

- **查询：** `Ad.find({ "rules.platform": "iOS" })`（直接用点符号查询，速度极快）。
    
- **优点：** 数据库只发一次指令，规则就跟着广告一起出来了。
    

---

## 2. 引用 (Referencing) 的代码实现

**场景：** “创建人”。一个管理员会创建成千上万个广告，如果把管理员名字嵌入每个广告，万一管理员改名，你要修改几万条数据。

### 定义 Schema

在 Mongoose 中，通过 `ref` 属性实现引用：

JavaScript

```
// 管理员集合
const AdminSchema = new mongoose.Schema({
    username: String,
    role: String
});
const Admin = mongoose.model('Admin', AdminSchema);

// 广告集合
const AdSchema = new mongoose.Schema({
    name: String,
    // 存储管理员的 ID
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Admin' // 关联到 Admin 模型
    }
});
const Ad = mongoose.model('Ad', AdSchema);
```

### 操作方式：使用 `.populate()`

引用最核心的技术是“填充”，它在查询时自动帮你把 ID 换成真正的文档内容：

JavaScript

```
// 在业务层查询时
const ads = await Ad.find()
    .populate('createdBy', 'username role') // 自动关联查询并只取用户名和角色
    .exec();

console.log(ads[0].createdBy.username); // 输出创建人的名字
```

---

## 3. 混合模式：生产环境的最优解

在实际大厂项目中，我们往往**既引用又嵌入**。这被称为 **Extended Reference Pattern（扩展引用模式）**。

**实际做法：**

在广告文档里，既存储 `createdBy` 的 ID（用于引用），也冗余存储一个 `creatorName`（用于展示）。

JavaScript

```
const AdSchema = new mongoose.Schema({
    name: String,
    createdBy: mongoose.Schema.Types.ObjectId, // 引用 ID，保证数据准确
    creatorName: String // 嵌入 冗余字段，保证查询展示时不用去查 Admin 表
});
```

- **查询时：** 直接显示 `creatorName`，极速响应。
    
- **管理员改名时：** 异步更新广告表中的 `creatorName`。虽然慢一点，但由于改名频率极低，完全可以接受。
    

---

## 4. 项目中的决策清单

当你写代码时，根据下表来写 `Schema`：

|**问自己：**|**选嵌入 (Embedding)**|**选引用 (Referencing)**|
|---|---|---|
|**子数据离开了父数据还有用吗？**|没用了（如广告的展示规则）|还有用（如广告引用的图片素材）|
|**子数据会被其他数据共享吗？**|不会|会（多个广告位共用同一个视频素材）|
|**子数据的数量级是多少？**|固定的几个|可能会很多（如广告的点击点击流水日志）|
|**对数据一致性要求高吗？**|高（必须同时成功/失败）|较低（允许一定的同步延迟）|

---

## 5. 总结：开发习惯建议

1. **默认先考虑嵌入**：这符合 MongoDB 的设计初衷，能让你的 API 响应最快。
    
2. **遇到以下情况再考虑拆分（引用）**：
    
    - 文档体积接近 16MB。
        
    - 数据需要在多个地方同步更新。
        
    - 需要对子数据进行独立的分页查询。
        

**既然学会了数据建模，你想看看如何配合之前说的 `express-validator`，写一个包含“关联 ID 合法性校验”的广告保存接口吗？**