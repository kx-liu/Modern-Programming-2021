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

class DataAnalysis:
    '''
    数据分析类，
    提供数据的读取及基本的时间（如某区域某类型排放随时间的变化）
    和空间分析（某一年全国排放的空间分布态势）方法
    '''
    def __init__(self, path):
        self.path = path
    
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
        _names["province"] = list(_names["province"])#; print(_names["province"])
        _names["industry"] = list(_names["industry"])#; print(_names["industry"])
        _names["type"] = list(_names["type"])
        self._names = _names
        self._error_province = list(_error_province)
    
    def __check_null(self, value, year, province, type, industry=None, mode=1):
        if value == "":
            raise NotNumError(year, province, type, industry, mode)
    
    def __interpolation(self, data_list):
        data_list_pd = pd.Series(data_list)
        data_list_pd = data_list_pd.interpolate()
        data_list_pd.dropna(inplace=True)
        return data_list_pd.tolist()
    
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
                        if province == "Sum-CO2": continue
                        province_data = _datasets[year]["Total"][province]["Total"]
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
                        industry_data_list = DataAnalysis.__interpolation(self, industry_data_list)
                        print(industry_data_list)
                    return industry_data_list
    
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

class DAVisualization(DataAnalysis):
    '''
    数据可视化类，以提供上述时空分析结果的可视化
    '''
    def line_chart(self, province=None, type=None, industry=None, start=1997, end=2015):
        time_list = [i for i in range(start, end+1)]
        if province == "All":
            # 总CO2排量时序图
            y = DataAnalysis.time_analysis(self, province="All")
            plt.plot(time_list, y)
            plt.title("总CO2排量时序图")
            filename = f"总CO2排量时序图.jpg"
        elif province == None:
            # 某type排量时序图
            y = DataAnalysis.time_analysis(self, type=type)
            plt.plot(time_list, y)
            plt.title(f"{type}排量时序图")
            filename = f"{type}排量时序图.jpg"
        else:
            if type == None:
                # 某省总CO2排量时序图
                y = DataAnalysis.time_analysis(self, province=province)
                plt.plot(time_list, y)
                plt.title(f"{province}总CO2排量时序图")
                filename = f"{province}总CO2排量时序图.jpg"
            else:
                if industry == None:
                    # 某省某type排量时序图
                    y = DataAnalysis.time_analysis(self, province=province, type=type)
                    plt.plot(time_list, y)
                    plt.title(f"{province}, {type!r}排量时序图")
                    filename = f"{province}, {type!r}排量时序图.jpg"
                else:
                    # 某省某type某industry排量时序图
                    y = DataAnalysis.time_analysis(self, province=province, type=type, industry=industry)
                    plt.plot(time_list, y)
                    plt.title(f"{province}, {type!r}, {industry!r}排量时序图")
                    filename = f"{province}, {type!r}, {industry!r}排量时序图.jpg"
        plt.xlabel("时间"); plt.ylabel("CO2排量")
        plt.xticks(rotation=30)
        ax = plt.gca()
        x_major_locator = MultipleLocator(1)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.savefig(filename, dpi=1000)
        plt.show()

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
                explode.append(ls[i] / max(ls) / 8)
            explode = tuple(explode)
            colors = np.flipud(cm.rainbow(np.arange(len(ls))/len(ls)))
            ax1.pie(ls, explode=explode, labels=labels, 
                    autopct='%1.0f%%', colors=colors, startangle=180)
            plt.savefig(filename, dpi=1000)
            plt.show()
        except MyZeroDivisionError as mzdve:
            print(mzdve.message)
            sys.exit(0)

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