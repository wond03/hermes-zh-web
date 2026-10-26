#!/usr/bin/env python3
"""把插件市场的英文简介翻成中文，产出 en -> zh 映射（catalog_zh.json）。

分批调用 DeepSeek，逐批落盘，中断后重跑会跳过已翻部分。
"""
import json, os, sys, time, re
import requests

KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API = "https://api.deepseek.com/chat/completions"
SRC = "/root/.codebuddy/artifact/catalog_desc.json"
OUT = "/root/.codebuddy/artifact/catalog_zh.json"
BATCH = 10

PROMPT = """你是技术文档翻译。把下面的插件简介逐条翻译成简体中文。

要求：
1. 保持原有顺序和条数，输出 JSON 数组，元素是字符串，长度与输入一致
2. 保留：产品名/插件名/公司名、URL、代码片段、命令、文件路径、环境变量名、版本号、缩写（MCP、API、CLI、SDK 等）
3. 语气平实，像产品说明，不要营销腔，不要加"该插件"之类冗余前缀
4. 只输出 JSON 数组，不要解释

输入：
"""


def call(batch):
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你只输出合法 JSON，不要 markdown 代码块。"},
            {"role": "user", "content": PROMPT + json.dumps(batch, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }
    r = requests.post(API, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=180)
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"].strip()
    txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.M).strip()
    return json.loads(txt)


def main():
    items = json.load(open(SRC, encoding="utf-8"))
    done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    todo = [s for s in items if s not in done]
    print(f"总 {len(items)}，已翻 {len(done)}，待翻 {len(todo)}", flush=True)

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        for attempt in range(3):
            try:
                zh = call(chunk)
                if len(zh) != len(chunk):
                    raise ValueError(f"长度不符 {len(zh)} != {len(chunk)}")
                for en, cn in zip(chunk, zh):
                    if cn and cn.strip() and cn.strip() != en.strip():
                        done[en] = cn.strip()
                json.dump(done, open(OUT, "w"), ensure_ascii=False, indent=1)
                print(f"  {i + len(chunk)}/{len(todo)} ok", flush=True)
                break
            except Exception as e:
                print(f"  {i} 第 {attempt + 1} 次失败: {type(e).__name__}: {str(e)[:120]}", flush=True)
                time.sleep(2 * (attempt + 1))
        else:
            print(f"  跳过批次 {i}", flush=True)

    print(f"完成：{len(done)} 条", flush=True)


if __name__ == "__main__":
    main()
