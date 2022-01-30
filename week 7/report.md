## 第七次作业 异常处理——Excel文件简单处理

### 7.1 大致框架

```python
class NotNumError(ValueError):
    '''
    若取到的一列数据中包含nan，则抛出该异常，并提供异常相关的年份，省份，工业和排放类型等信息。
    在此基础上，利用try except捕获该异常，打印异常信息，并对应位置的数据进行适当的填充。
    '''
class MyZeroDivisionError(ZeroDivisionError):
    '''
    由于部分省份排放总量数据为0，要求在计算比例时进行检验，
    若检验发现总量为0，则抛出ZeroDivisionError，并打印对应的行名等信息。
    '''
class DataAnalysis:
    '''
    数据分析类，
    提供数据的读取及基本的时间（如某区域某类型排放随时间的变化）
    和空间分析（某一年全国排放的空间分布态势）方法
    '''
class DAVisualization(DataAnalysis):
    '''
    数据可视化类，
    以提供上述时空分析结果的可视化
    '''
```

### 7.2 NotNumError类

- 继承`ValueError`类，自定义其错误信息的输出；

```python
class NotNumError(ValueError):
    '''
    若取到的一列数据中包含nan，则抛出该异常，并提供异常相关的年份，省份，工业和排放类型等信息。
    在此基础上，利用try except捕获该异常，打印异常信息，并对应位置的数据进行适当的填充。
    '''
    def __init__(self, year, province, type, industry, mode=1):
        self.year = year
        self.industry = industry
        self.province = province
        self.type = type
        if mode == 0:
            self.message = f"Not-Number error in colume year {year!r}, province {province!r}, 'Sum sheet', type {type!r}"
        if mode == 1:
            self.message = f"Not-Number error in colume year {year!r}, province {province!r}, type {type!r}, industry {industry!r}"
```

- 其中`mode`区分其读入的sheet为Sum或其他具体省份，输出结果不尽相同。

### 7.3 DataAnalysis类

#### 7.3.0 DataAnalysis.\_\_init\__

```python
def __init__(self, path):
    self.path = path
```

- 该类实例化时应当提供原始数据的路径`path`。

#### 7.3.1 DataAnalysis.load_files

```python
def load_files(self):
    file_list = os.listdir(self.path)
    _wbs = []
    row_index_sum = [i for i in range(1, 31)] + [32]
    col_index_sum = [i for i in range(1, 20)]
    row_index = [i for i in range(4, 51)]
    col_index = [i for i in range(1, 20)]
    _datasets = {}
    _names = {"province": set(), "industry": set(), "type": set()}
    _error_province = set()
    with open("ErrorLog.txt", "w") as f:
        for file in file_list:
            year = int(file[-9:-5])
            wb = xlrd.open_workbook(self.path + "\\" + file)
            _wbs.append(wb)
            sheet_names = wb.sheet_names()
            _datasets[year] = {}
            for sheet in sheet_names:
                data = wb.sheet_by_name(sheet)
                if sheet == "Sum":
                    _datasets[year]["Total"] = {}
                    for i in row_index_sum:
                        province = data.cell(i, 0).value
                        _names["province"].add(province)
                        _datasets[year]["Total"][province] = {}
                        for j in col_index_sum:
                            type = data.cell(0, j).value
                            _names["type"].add(type)
                            _datasets[year]["Total"][province][type] = data.cell(i, j).value
                            try:
                                DataAnalysis.__check_null(self, data.cell(i, j).value, \
                                                          year, province, type, mode=0)
                            except NotNumError as nne:
                                f.write(nne.message+"\n")
                                _datasets[year]["Total"][province][type] = np.nan
                                _error_province.add(province)
                else:
                    province = sheet
                    _names["province"].add(province)
                    _datasets[year][province] = {}
                    for j in col_index:
                        type = data.cell(0, j).value
                        _names["type"].add(type)
                        _datasets[year][province][type] = {}
                        for i in row_index:
                            industry = data.cell(i, 0).value.strip()
                            _names["industry"].add(industry)
                            _datasets[year][province][type][industry] = data.cell(i, j).value
                            try:
                                DataAnalysis.__check_null(self, data.cell(i, j).value, \
                                                       year, province, type, industry, 1)
                            except NotNumError as nne:
                                f.write(nne.message+"\n")
                                _datasets[year][province][type][industry] = np.nan
                                _error_province.add(province)
    self._datasets = _datasets
    self._wbs = _wbs
    _names["province"] = list(_names["province"])
    _names["industry"] = list(_names["industry"])
    _names["type"] = list(_names["type"])
    self._names = _names
    self._error_province = list(_error_province)
```

******

- 存储全部数据的数据结构，由`datasets`字典完成存储：

```python
datasets = {
    1997:{
        "Total":{
            "Beijing":{
                "Total": total, 
                "Raw Coal": tot1,
                "Cleaned Coal": tot2
                # ...
            	},
            # "Tianjin": ...
        }
        "Beijing":{
            "Raw Coal": {
                "Farming, Forestry...": x1
                "Coal Mining...": x2
                # ...
            	}
        # "Tianjin"...
        }
    }
    # 1998: ...
}
```

******

- 单元格是否为空由私有方法`__check_null`识别，并用`np.nan`填充，方便绘制图形时的插值处理。

#### 7.3.2 DataAnalysis.__check_null

```python
def __check_null(self, value, year, province, type, industry=None, mode=1):
    if value == "":
        raise NotNumError(year, province, type, industry, mode)
```

- 若单元格为空值，`raise NotNumError(...)`，由`load_files`方法中的`try-except`接住。

#### 7.3.3 DataAnalysis.__interpolation

```python
def __interpolation(self, data_list):
    data_list_pd = pd.Series(data_list)
    data_list_pd = data_list_pd.interpolate()
    data_list_pd.dropna(inplace=True)
    return data_list_pd.tolist()
```

- 对`np.nan`进行插值处理。

#### 7.3.4 DataAnalysis.time_analysis

```python
def time_analysis(self, province=None, type=None, industry=None, start=1997, end=2015):
    _datasets = self._datasets
    _names = self._names
    time_list = [i for i in range(start, end+1)]
    if province == "All":
        if type == "All":
            # 总CO2各省饼图
            province_data_list = []
            for year in time_list:
                for province in _names["province"]:
                    province_data = _datasets[year][province]["Total"]
                    province_data_list.append(province_data)
            return province_data_list
        else:
            # 总CO2排量时序图
            Sum_CO2_list = []
            for year in time_list:
                Sum_CO2 = _datasets[year]["Total"]["Sum-CO2"]["Total"]
                Sum_CO2_list.append(Sum_CO2)
            assert len(Sum_CO2_list) == len(time_list)
            return Sum_CO2_list
    elif province == None:
        if type == "All":
            # 总CO2各type饼图
            type_data_list = []
            for year in time_list:
                for type in _names["type"]:
                    if type == "Total": continue
                    type_data = _datasets[year]["Total"]["Sum-CO2"][type]
                    type_data_list.append(type_data)
            return type_data_list
        else:
            # 某type排量时序图
            type_data_list = []
            for year in time_list:
                type_data = _datasets[year]["Total"]["Sum-CO2"][type]
                type_data_list.append(type_data)
            assert len(type_data_list) == len(time_list)
            return type_data_list
    else:
        if type == None:
            # 某省总CO2排量时序图
            province_data_list = []
            for year in time_list:
                province_data = _datasets[year]["Total"][province]["Total"]
                province_data_list.append(province_data)
            assert len(province_data_list) == len(time_list)
            return province_data_list
        else:
            if industry == None:
                # 某省某type排量时序图
                type_data_list = []
                for year in time_list:
                    type_data = _datasets[year]["Total"][province][type]
                    type_data_list.append(type_data)
                assert len(type_data_list) == len(time_list)
                return type_data_list
            elif industry == "All":
                # 某省某type各industry饼图
                industry_data_list = []
                for year in time_list:
                    for industry in _names["industry"]:
                        if industry == "Total Consumption": continue
                        industry_data = _datasets[year][province][type][industry]
                        industry_data_list.append(industry_data)
                return industry_data_list
            else:
                # 某省某type某industry排量时序图
                industry_data_list = []
                for year in time_list:
                    industry_data = _datasets[year][province][type][industry]
                    industry_data_list.append(industry_data)
                assert len(industry_data_list) == len(time_list)
                print(industry_data_list)
                if pd.isnull(industry_data_list).any():
                    industry_data_list = DataAnalysis.interpolation(self, industry_data_list)
                    print(industry_data_list)
                return industry_data_list
```

- 定义了8种数据级别，其中5种为折现时序图，3种为截面饼图：
  - 总$CO_2$各省饼图
  - 总$CO_2$各type饼图
  - 某省某type各industry饼图
  - 总$CO_2$排量时序图
  - 某type排量时序图
  - 某省总$CO_2$排量时序图
  - 某省某type排量时序图
  - 某省某type某industry排量时序图

- 时序图返回指定年份区间的时序数据，饼图返回指定年份的截面数据；
- 其中对某省某type某industry通过`pd.isnull().any()`进行缺失值判断，若`True`则通过私有方法`__interpolation`进行插值；
- 这里反思做的不好的一点，做完才意识到Sheet Sum中的数据体现不出缺失值，而在做折线图与饼图的数据处理时基本用的均为Sum中的数据，仅有某省某type某industry排量时序图用到了Sheet中其余省份的数据，事实上应当读取省份数据后将Sum中数据进行覆盖，对应缺失值才可体现。

#### 7.3.4 DataAnalysis.spacial_analysis

```python
def spacial_analysis(self, year):
    province_dic = {
        'Beijing': '北京', 'Tianjin': '天津', 'Hebei': '河北', 'Shanxi': '山西', 
        'InnerMongolia': '内蒙古', 'Liaoning': '辽宁', 'Jilin': '吉林', 
        'Heilongjiang': '黑龙江', 'Shanghai': '上海', 'Jiangsu': '江苏', 
        'Zhejiang': '浙江', 'Anhui': '安徽', 'Fujian': '福建', 'Jiangxi': '江西', 
        'Shandong': '山东', 'Henan': '河南', 'Hubei': '湖北', 'Hunan': '湖南', 
        'Guangdong': '广东', 'Guangxi': '广西', 'Hainan': '海南', 'Chongqing': '重庆', 
        'Sichuan': '四川', 'Guizhou': '贵州', 'Yunnan': '云南', 'Shaanxi': '陕西', 
        'Gansu': '甘肃', 'Qinghai': '青海', 'Ningxia': '宁夏', 'Xinjiang': '新疆'
    }
    data = []
    for province in self._names["province"]:
        if province == "Sum-CO2": continue
        province_data = DataAnalysis.time_analysis(self, province=province)
        data.append([province_dic[province], province_data[year-1997]])
    return data
```

- 返回的数据结构为`[["北京", x1], ["天津", x2], ...]`，以便`pyecharts`绘制地图。

### 7.4 MyZeroDivisionError类

```python
class MyZeroDivisionError(ZeroDivisionError):
    '''
    由于部分省份排放总量数据为0，要求在计算比例时进行检验，
    若检验发现总量为0，则抛出ZeroDivisionError，并打印对应的行名等信息。
    '''
    def __init__(self, year, province, type):
        self.year = year
        self.province = province
        self.type = type
        self.message = f"ZeroDivisionError in year {year!r}, province {province!r}, type {type!r}, therefore can\'t draw a pie chart."
```

- 继承`ZeroDivisionError`类，若饼图的数据是否均为零则报错，打印具体信息。

### 7.5 DAVisualization类

- 继承了`DataAnaylsis`类

#### 7.5.1 DAVisualization.line_chart

```python
def line_chart(self, province=None, type=None, industry=None, start=1997, end=2015):
    time_list = [i for i in range(start, end+1)]
    if province == "All":
        # 总CO2排量时序图
        y = DataAnalysis.time_analysis(self, province="All")
        plt.plot(time_list, y)
    elif province == None:
        # 某type排量时序图
        y = DataAnalysis.time_analysis(self, province="All")
        plt.plot(time_list, y)
    else:
        if type == None:
            # 某省总CO2排量时序图
            y = DataAnalysis.time_analysis(self, province=province)
            plt.plot(time_list, y)
        else:
            if industry == None:
                # 某省某type排量时序图
                y = DataAnalysis.time_analysis(self, province=province, type=type)
                plt.plot(time_list, y)
            else:
                # 某省某type某industry排量时序图
                y = DataAnalysis.time_analysis(self, province=province, type=type, industry=industry)
                plt.plot(time_list, y)
    plt.show()
```

- 总$CO_2$排量时序图

![](https://s2.loli.net/2022/01/29/5UTD4VxnSeKbjdc.jpg)

- 某type排量时序图

![](https://s2.loli.net/2022/01/29/R4enHw9f5QW2l8y.jpg)

- 某省总$CO_2$排量时序图

![](https://s2.loli.net/2022/01/29/R4enHw9f5QW2l8y.jpg)

- 某省某type排量时序图

![](https://s2.loli.net/2022/01/29/xGnNQIwqAvy8HUC.jpg)

- 某省某type某industry排量时序图

![](https://s2.loli.net/2022/01/29/SdrBWD4xp958JOz.png)

#### 7.5.2 DAVisualization.pie_chart

```python
def pie_chart(self, province=None, type=None, industry=None, year=2015):
    try:
        fig1, ax1 = plt.subplots(figsize=(10,10))
        if province == "All":
            # 总CO2各省饼图
            ls = DataAnalysis.time_analysis(self, province="All", type="All", start=year, end=year)
            labels = self._names["province"]
            labels.remove("Sum-CO2")
            ax1.set_title(f"{year}年总CO2各省饼图", fontsize=16)
            filename = f"{year}年总CO2各省饼图.jpg"
        else:
            if type == "All":
                # 总CO2各type饼图
                ls = DataAnalysis.time_analysis(self, type="All", start=year, end=year)
                labels = self._names["type"]
                labels.remove("Total")
                ax1.set_title(f"{year}年总CO2各type饼图", fontsize=16)
                filename = f"{year}年总CO2各type饼图.jpg"
            else:
                # 某省某type各industry饼图
                ls = DataAnalysis.time_analysis(self, province=province, type=type, industry="All", start=year, end=year)
                if sum(ls) == 0:
                    raise MyZeroDivisionError(year=year, province=province, type=type)
                labels = self._names["industry"]
                ax1.set_title(f"{year}年{province!r}, {type!r}各industry饼图", fontsize=16)
                filename = f"{year}年{province!r}, {type!r}各industry饼图.jpg"
        zipped = dict(sorted(zip(ls, labels), key=lambda x:x[0], reverse=True))
        ls = list(zipped.keys())
        labels = list(zipped.values())
        explode = []
        for i in range(len(ls)):
            explode.append(ls[i] / max(ls) / 4)
        explode = tuple(explode)
        colors = np.flipud(cm.rainbow(np.arange(len(ls))/len(ls)))
        ax1.pie(ls, explode=explode, labels=labels, 
                autopct='%1.0f%%', colors=colors, startangle=180)
        plt.savefig(filename, dpi=1000)
        plt.show()
    except MyZeroDivisionError as mzdve:
        print(mzdve.message)
        sys.exit(0)
```

- 总$CO_2$各省饼图

![](https://s2.loli.net/2022/01/29/deHKwPaVpNmzgTS.jpg)

- 总$CO_2$各type饼图

![](https://s2.loli.net/2022/01/29/XjydzRvYpHnLD9l.jpg)

- 某省某type各industry饼图

  ![](https://s2.loli.net/2022/01/29/TCGvlt9EN7aUuAL.png)

  - 其中，存在`values`全为0的情况，此时`pie_chart`无法绘制，则抛出`MyZeroDivisionError`错误，打印错误信息；
  - 例如`da.pie_chart(province="Beijing", type="Other Petroleum Products", year=1997)`，即1997年北京`type="Other Petroleum Products"`下的`industry`数据均为0，此时报出如下错误：`ZeroDivisionError in year 1997, province 'Beijing', type 'Other Petroleum Products', therefore can't draw a pie chart.`

#### 7.5.3 DAVisualization.map_chart

```python
def map_chart(self, start=1997, end=2015):
    tl = Timeline()
    time_list = list(range(start, end+1))
    for year in time_list:
        data = DataAnalysis.spacial_analysis(self, year)
        m = Map()
        m.add(year, data, "china")
        m.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        m.set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年全国CO2排量"),
            visualmap_opts=opts.VisualMapOpts(max_=800), 
        )
        tl.add(m, year)
    tl.render(f"{start}-{end}年全国CO2排量.html")
```

<img src="https://s2.loli.net/2022/01/29/lSHBv2gCfNhJy3X.png" style="zoom:40%;" />

<img src="https://s2.loli.net/2022/01/29/bPQH34DydCxKzLa.png" style="zoom:40%;" />

### 7.6 包管理与main函数

```python
import xlrd
import os
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib import font_manager as fm
from matplotlib import cm
plt.style.use('ggplot')
import numpy as np
import pandas as pd
from pyecharts.charts import Map
from pyecharts import options as opts
from pyecharts.charts import Timeline
import sys

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    da = DAVisualization("D:\\vscode py\\现代程设\\week 7\\co2_demo\\")
    da.load_files()

    # 总CO2排量时序图
    # da.line_chart(province="All")
    
    # 某type排量时序图
    # da.line_chart(type="Raw Coal")

    # 某省总CO2排量时序图
    # da.line_chart(province="Beijing")

    # 某省某type排量时序图
    # da.line_chart(province="Hebei", type="Raw Coal")

    # 某省某type某industry排量时序图
    # da.line_chart(province="Ningxia", type="Raw Coal", industry="Production and Supply of Electric Power, Steam and Hot Water", start=1997, end=2015)
    
    # 总CO2各省饼图
    # da.pie_chart(province="All")
    
    # 总CO2各type饼图
    # da.pie_chart(type="All", year=2000)

    # 某省某type各industry饼图
    # da.pie_chart(province="Henan", type="Raw Coal", year=2008)
    
    # 某省某type各industry饼图(error)
    # da.pie_chart(province="Beijing", type="Other Petroleum Products", year=1997)

    # 地图
    # da.map_chart(start=1997, end=2015)

if __name__ == '__main__':
    main()
```

### 7.7 时间趋势

- 从以上折线图可以看出，2011年作为$CO_2$排放的转折点，总$CO_2$排放迎来拐点，即从1997-2011年的直线增长势头趋于平缓，而重工业行业与部分省份$CO_2$排放开始下降，碳排放治理卓有成效。
