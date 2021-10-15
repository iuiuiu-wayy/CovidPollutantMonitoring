from datetime import date
def strdate2date(strdate):
    y = int(strdate.split("-")[0])
    m = int(strdate.split("-")[1])
    d =  int(strdate.split("-")[2].split('T')[0])
    return date(y,m,d)