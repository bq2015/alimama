# alimama

自动登录阿里妈妈，采集淘宝客商品推广信息

> 搜索商品，获取推广码
> 搜索店铺，获取热销单品，获取推广码

### pip

- python3.6
- requests
- selenium
- phantomjs 


### mind flow
 
打开阿里妈妈登录页 -- 登录用户 -- 跳转到阿里妈妈后台  -- 获取商品List -- 查询商品推广数据

### How to use?
 ```python
 python3 alimama.py username password


 ```
###

> 隐藏浏览器， 隐藏执行
```javascript
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu') 
```