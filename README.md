# crawl_holiday_workday
爬取法定节假日、法定工作日(补假日)，生成golang代码。可准确判断某天是节假日，还是工作日

## Usage:
1. 每年会在10~11月公告下一年的法定假日，和补假日。将下一年的公告页面URL加入python脚本的`CHINA_HOLIDAY_WORKDAY_URLS`中，即可：
![image](https://user-images.githubusercontent.com/11456678/125760514-34d43454-fe43-4376-884e-18dc8ea00750.png)
2. 运行python脚本，生成golang代码
3. 将生成的golang代码放到项目中，使用如下两个函数，既可准确判断某天是节假日，还是工作日:
```golang
util.IsHoliday(time.Now())
util.IsWorkday(time.Now())
```
