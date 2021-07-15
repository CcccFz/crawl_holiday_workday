# crawl_holiday_workday
爬取法定节假日、法定工作日(补假日)，转换为golang代码。可准确判断某天是节假日，还是工作日。

## Usage:
运行python脚本，生成golang代码后：
```golang
util.IsHoliday(time.Now())
util.IsWorkday(time.Now())
```
