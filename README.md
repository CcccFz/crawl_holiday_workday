# crawl_holiday_workday
爬取法定节假日、法定工作日(补假日)，转换为golang代码。可准确判断某天是节假日，还是工作日。

## Usage:
1.  运行python脚本，生成golang代码
2.  将生成的golang代码放到项目中，使用如下两个函数
```golang
util.IsHoliday(time.Now())
util.IsWorkday(time.Now())
```
3. 每年会在10~11月公告下一年的法定假日，和补假日。将下一年的公告页面URL加入python脚本的`CHINA_HOLIDAY_WORKDAY_URLS`即可：
![image](https://user-images.githubusercontent.com/11456678/125760314-bb5d0e98-fca6-4bb6-b2c0-33be4131ead5.png)
