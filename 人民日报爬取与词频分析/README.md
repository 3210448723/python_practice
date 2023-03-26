# 参考

1. https://zhuanlan.zhihu.com/p/571501780

# 功能

1. `crawler.py` 文件是主程序，运行自动执行爬虫，爬取指定日期的 `人民日报` 并合并为一个PDF文件，之后计算词频，保存并发送分析结果

2. `cal_frequency.py` 文件用于计算词频，找出前50个主题词汇，以TF-IDF值降序排序

3. `save_results.py` 文件用于保存词频结果为csv格式

4. `send_result.py` 文件用于发送csv结果到目标邮箱，这里记得要改对应的参数

   ```python
   # 这些要改
   from_addr = 'xxx@qq.com'
   password = 'uiosslpxxx'  # 使用授权密码
   to_addr = 'xxx@qq.com'
   smtp_server = 'smtp.qq.com'
   ```

   