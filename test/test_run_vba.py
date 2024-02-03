# Author: Nike Liu
import win32com.client
from win32com.client import Dispatch, constants
filename = "D:/工作\报关快递单据/副本快递发货系统v1.0.xlsm"
xls = win32com.client.DispatchEx("Excel.Application")
xls.Workbooks.Open(Filename=filename)
xls.DisplayAlerts = 0
# xls.Run("access_test")
xls.Run("打开鉴定报告")
xls.Run("打开发票")