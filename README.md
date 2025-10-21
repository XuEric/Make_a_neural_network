# Make_a_neural_network
This is the code for the "Make a Neural Network" - Intro to Deep Learning #2 by Siraj Raval on Youtube

##Overview

This is the code for [this](https://youtu.be/p69khggr1Jo) video by Siraj Raval on Youtube. This is a [simple](http://computing.dcu.ie/~humphrys/Notes/Neural/single.neural.html) single layer feedforward neural network (perceptron). We use binary digits as our inputs and expect binary digits as our outputs. We'll use [backpropagation](http://neuralnetworksanddeeplearning.com/chap2.html) via gradient descent to train our network and make our prediction as accurate as possible.

##Dependencies

None! Just numpy.

##Usage

Run ``python demo.py`` in terminal to see it train, then predict.

##Challenge

The challenge for this video is to create a 3 layer feedforward neural network using only numpy as your dependency. By doing this, you'll understand exactly how backpropagation works and develop an intuitive understanding of neural networks, which will be useful for more the more complex nets we build in the future. Backpropagation usually involves recursively taking derivatives, but in our 1 layer demo there was no recursion so was a trivial case of backpropagation. In this challenge, there will be. Use a small binary dataset, you can define one programmatically like in this example.

**Bonus -- use a larger, more interesting dataset**

##Credits

The credits for this code go to [Milo Harper](https://github.com/miloharper). I've merely created a wrapper to get people started.


---

# Tools: AI 30天最热精选清单（新闻/论文/开源/模型）

全新 Python 3 工具已添加，位于 `tools/ai_hotlist/`，与原 Python2 演示互不影响。该工具可一键抓取过去 N 天的 AI 新闻、论文、开源项目与模型数据，进行去重、打分排序，并自动生成中文要点摘要与报告。

- 数据来源：
  - 新闻：若干 RSS 源（量子位、OpenAI/Google AI Blog 等，解析失败会自动跳过）
  - 论文：arXiv（cs.CL、cs.LG、cs.CV、cs.AI）+ Papers with Code Trending
  - 开源：GitHub Search（按 stars 排序，近 N 天 created）+ GitHub Trending（月度）
  - 模型/数据集：Hugging Face Hub 最近更新条目
- 输出：
  - 结构化数据：data/ai_hotlist_YYYYMMDD.json（以及原始 data/ai_hotlist_raw_YYYYMMDD.json）
  - 报告：reports/ai-hotlist-YYYYMMDD.md（中文摘要、亮点、链接与热度指标）
- 运行方式：
  - 依赖：`tools/ai_hotlist/requirements.txt`
  - 使用 Make：`make hotlist`
  - 或脚本：`bash tools/ai_hotlist/run_hotlist.sh --days 30`
  - 可选参数：
    - `--days` 时间窗口（默认 30）
    - `--allow` 关键词白名单（逗号分隔）
    - `--deny` 关键词黑名单（逗号分隔）
    - `--max-per-section` 每类目最大条数（默认 100）
    - 可通过环境变量 `GITHUB_TOKEN` 提升 GitHub API 速率

注意：本工具默认无需密钥即可运行基础功能；部分站点可能无可用 RSS，将被自动忽略。