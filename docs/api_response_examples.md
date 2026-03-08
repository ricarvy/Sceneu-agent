
### 1. 响应体示例 (Response Body Examples)

#### 情况 A: `seed_mode = "true"` (开启种草模式)

当 `seed_mode` 为 `"true"` 时，返回的 `generated_image_urls` 数组中将**包含**生成的订单截图 URL（以 `/static/generate/order_` 开头）。同时，AI 的回复内容（`content`）中也会通过 Markdown 图片链接展示这张截图。

```json
{
  "messages": [
    {
      "type": "human",
      "content": "..."
    },
    {
      "type": "ai",
      "content": "这件法式连衣裙太美了！✨ 面料质感超棒，穿上显瘦又高级，简直是约会神器！💖 姐妹们快冲！🔥 #OOTD #法式穿搭\n\n![](https://ark.volccdn.com/obj/eden-cn/lkpkbnumll/ljhwZthlaukjlkulzlp/generated_image_1.png)\n![](http://host:8888/static/generate/order_a1b2c3d4.png)"
    }
  ],
  "run_id": "xxx-xxx-xxx",
  "generated_image_urls": [
    "https://ark.volccdn.com/obj/eden-cn/lkpkbnumll/ljhwZthlaukjlkulzlp/generated_image_1.png",
    "http://host:8888/static/generate/order_a1b2c3d4.png"  <-- 注意这里多了订单截图
  ]
}
```

#### 情况 B: `seed_mode = "false"` (关闭种草模式 - 默认)

当 `seed_mode` 为 `"false"`（或未传）时，返回的 `generated_image_urls` 数组中**只包含** AI 生成的营销场景图，**不包含**订单截图。

```json
{
  "messages": [
    {
      "type": "human",
      "content": "..."
    },
    {
      "type": "ai",
      "content": "这件法式连衣裙太美了！✨ 面料质感超棒，穿上显瘦又高级，简直是约会神器！💖 姐妹们快冲！🔥 #OOTD #法式穿搭\n\n![](https://ark.volccdn.com/obj/eden-cn/lkpkbnumll/ljhwZthlaukjlkulzlp/generated_image_1.png)"
    }
  ],
  "run_id": "xxx-xxx-xxx",
  "generated_image_urls": [
    "https://ark.volccdn.com/obj/eden-cn/lkpkbnumll/ljhwZthlaukjlkulzlp/generated_image_1.png"
  ]
}
```

### 2. 核心区别

| 字段 | `seed_mode="true"` | `seed_mode="false"` |
| :--- | :--- | :--- |
| **generated_image_urls** | 包含 `https://ark...` (AI图) **+** `http://.../order_xxx.png` (订单图) | 仅包含 `https://ark...` (AI图) |
| **AI 回复内容** | 文案后会附带 AI 图和**订单截图**的 Markdown 链接 | 文案后仅附带 AI 图的 Markdown 链接 |
| **触发条件** | 请求中传入 `seed_mode="true"` 且必须包含 `店铺名` 和 `价格` | 请求中 `seed_mode="false"` 或缺省 |
